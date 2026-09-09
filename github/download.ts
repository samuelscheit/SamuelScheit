import * as fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { config } from "dotenv";
import cliProgress from "cli-progress";
import PQueue from "p-queue";
import {
	createGitHubRepositoryMetadata,
	createGitHubTimelinePageData,
	type GitHubCommit,
	type GitHubExport,
	type GitHubRepositoryDetails,
} from "./page-data";

config();

const TOKEN = process.env.GH_TOKEN;
const CLI_LOGIN = process.argv.slice(2).find((argument) => !argument.startsWith("-"));
const LOGIN = process.env.GITHUB_LOGIN || CLI_LOGIN || "samuelscheit";
const SCRIPT_DIRECTORY = path.dirname(fileURLToPath(import.meta.url));
const TIMELINE_OUTPUT_FILE = path.join(SCRIPT_DIRECTORY, "timeline.json");
const REPOSITORIES_OUTPUT_FILE = path.join(SCRIPT_DIRECTORY, "repositories.json");

const EXCLUDED_REPOS = [
	"respondchat/assets",
	"SamuelScheit/rumble-rabbi",
	"SamuelScheit/assets",
	"SamuelScheit/discord-nitro-client",
	"SamuelScheit/twitch-viewer-bot",
	"SamuelScheit/clickfarm",
	"SamuelScheit/cryars",
	"SamuelScheit/SamuelScheit",
	"SamuelScheit/whatsapp-tracker",
];
const EXCLUDED_REPO_KEYS = new Set(EXCLUDED_REPOS.map((repository) => repository.toLowerCase()));

// GitHub returns a top-level FORBIDDEN error for
// `commitContributionsByRepository` when even one of the user's contributed
// repositories belongs to an organization that blocks classic PATs.  Keep
// those organizations out of discovery up front.  ExodusMovement is the
// known blocked organization for the token used by this downloader. Additional
// organizations can be supplied through GITHUB_EXCLUDED_ORGS.
const EXCLUDED_ORGS = new Set(
	[
		"ExodusMovement",
		...(process.env.GITHUB_EXCLUDED_ORGS || "")
			.split(",")
			.map((org) => org.trim())
			.filter(Boolean),
	].map((org) => org.toLowerCase()),
);

function isExcludedRepository(repository: string): boolean {
	const [owner] = repository.split("/", 1);
	return EXCLUDED_REPO_KEYS.has(repository.toLowerCase()) || EXCLUDED_ORGS.has(owner.toLowerCase());
}

interface Repository {
	nameWithOwner: string;
}

interface YearsData {
	user: {
		id: string;
		contributionsCollection: {
			contributionYears: number[];
		};
	};
}

interface WindowData {
	user: {
		contributionsCollection: {
			commitContributionsByRepository: Array<{ repository: Repository }>;
		};
	};
}

interface GraphQLResponse<T> {
	data: T;
	errors?: any[];
}

// Function parameter and return types
const yearsQuery = `
  query ($login: String!) {
    user(login: $login) {
	  id
      contributionsCollection { contributionYears }
    }
  }`;

const windowQuery = `
  query ($login: String!, $from: DateTime!, $to: DateTime!) {
    user(login: $login) {
      contributionsCollection(from: $from, to: $to) {
        commitContributionsByRepository(maxRepositories: 100) {
          repository { nameWithOwner }
        }
      }
    }
  }`;

const refsQuery = `
  query ($owner: String!, $name: String!, $refCursor: String) {
    repository(owner: $owner, name: $name) {
      refs(first: 100, refPrefix: "refs/heads/", after: $refCursor) {
        nodes { name }
        pageInfo { hasNextPage endCursor }
      }
    }
  }`;

const commitsByRefQuery = `
  query (
    $owner: String!
    $name: String!
    $ref:  String!
    $authorId: ID!
    $cursor: String
  ) {
    repository(owner: $owner, name: $name) {
      ref(qualifiedName: $ref) {
        target {
          ... on Commit {
            history(first: 100, after: $cursor, author: {id: $authorId}) {
              edges {
                node {
                  oid
                  messageHeadline
                  committedDate
                }
              }
              pageInfo { hasNextPage endCursor }
            }
          }
        }
      }
    }
  }`;

const repositoryDetailsQuery = `
  query ($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      id
      name
      nameWithOwner
      description
      url
      homepageUrl
      createdAt
      isPrivate
      isFork
      forkCount
      stargazerCount
      primaryLanguage {
        name
        color
      }
      owner {
        login
      }
      openGraphImageUrl
    }
  }`;

export async function ghRequest(query: string, variables: Record<string, any>, retries = 3): Promise<any> {
	for (let attempt = 0; attempt < retries; attempt++) {
		try {
			const res = await fetch("https://api.github.com/graphql", {
				method: "POST",
				headers: {
					Authorization: `bearer ${TOKEN}`,
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ query, variables }),
			});

			const bodyText = await res.text();
			let json: GraphQLResponse<any>;
			try {
				json = JSON.parse(bodyText) as GraphQLResponse<any>;
			} catch (parseError) {
				const preview = bodyText.replace(/\s+/g, " ").trim().slice(0, 200);
				throw new Error(`Failed to parse JSON response (${res.status} ${res.statusText}). Body preview: ${preview || "<empty>"}`);
			}

			if (!res.ok) {
				throw new Error(`GitHub API responded ${res.status} ${res.statusText}`);
			}

			// Check for rate limiting
			if (json.errors && json.errors.some((error: any) => error.type === "RATE_LIMITED")) {
				const resetTime = res.headers.get("x-ratelimit-reset");
				const waitTime = resetTime ? parseInt(resetTime) * 1000 - Date.now() + 60000 : 60000; // Add 1 minute buffer

				console.log(`⚠️  Rate limited. Waiting ${Math.ceil(waitTime / 1000)} seconds...`);
				await new Promise((resolve) => setTimeout(resolve, waitTime));
				continue;
			}

			if (json.errors) throw new Error(JSON.stringify(json.errors));
			return json.data;
		} catch (error) {
			const message = error instanceof Error ? error.message : String(error);
			const attemptLabel = `attempt ${attempt + 1}/${retries}`;
			// FORBIDDEN is deterministic for this token/repository. Retrying it
			// only delays the window bisection that recovers other repositories.
			if (isForbiddenError(error)) throw error;
			if (attempt === retries - 1) {
				console.log(`❌ Request failed, no more retries (${attemptLabel})`, message, query, variables);
				throw error;
			}
			console.log(`⚠️  Request failed, retrying in 5 seconds... (${attemptLabel})`, message, query, variables);
			await new Promise((resolve) => setTimeout(resolve, 5000));
		}
	}
}

export async function fetchRepositoryDetails(owner: string, name: string): Promise<GitHubRepositoryDetails | null> {
	try {
		const data = await ghRequest(repositoryDetailsQuery, { owner, name });
		return data.repository;
	} catch (error) {
		console.log(`⚠️  Failed to fetch repository details for ${owner}/${name}:`, error);
		return null;
	}
}

export async function fetchCommits(owner: string, name: string, authorId: string, progressBar?: cliProgress.SingleBar) {
	const commitsMap = new Map<string, GitHubCommit>();

	let totalCommits = 0;
	let processedRefs = 0;

	// Fetch all refs with pagination to avoid heavy queries
	const refNames: string[] = [];
	let refCursor: string | null = null;
	while (true) {
		const refsData = await ghRequest(refsQuery, { owner, name, refCursor });
		const refsConn = refsData.repository?.refs;
		if (!refsConn?.nodes?.length) break;
		refsConn.nodes.forEach((node: any) => refNames.push(node.name));
		if (!refsConn.pageInfo?.hasNextPage) break;
		refCursor = refsConn.pageInfo.endCursor;
		// Add small delay between requests
		await new Promise((resolve) => setTimeout(resolve, 100));
	}

	const totalRefs = refNames.length;
	// Update progress bar total if provided
	if (progressBar) {
		progressBar.setTotal(totalRefs);
	}

	if (!totalRefs) {
		return [];
	}

	// Process each ref individually
	for (const refName of refNames) {
		let refCommits = 0;
		let commitCursor: string | null = null;

		while (true) {
			const commitData = await ghRequest(commitsByRefQuery, {
				owner,
				name,
				ref: `refs/heads/${refName}`,
				authorId,
				cursor: commitCursor,
			});

			const history = commitData.repository?.ref?.target?.history;
			if (!history) break;

			if (history.edges) {
				history.edges.forEach((e: any) => {
					const { oid, messageHeadline, committedDate } = e.node;
					if (!commitsMap.has(oid)) {
						commitsMap.set(oid, {
							oid,
							messageHeadline,
							committedDate,
						});
						totalCommits++;
						refCommits++;
					}
				});
			}

			if (!history.pageInfo?.hasNextPage) break;
			commitCursor = history.pageInfo.endCursor;
			// Add small delay between requests
			await new Promise((resolve) => setTimeout(resolve, 100));
		}

		processedRefs++;
		// Update progress bar with current ref and commit info
		if (progressBar) {
			progressBar.update(processedRefs, {
				ref: refName,
				commits: refCommits,
				totalCommits: totalCommits,
			});
		}
	}

	return Array.from(commitsMap.values());
}

function isForbiddenError(error: unknown): boolean {
	return /(?:FORBIDDEN|forbids access)/i.test(String(error instanceof Error ? error.message : error));
}

/**
 * Discover repositories for a time window. GitHub evaluates
 * commitContributionsByRepository as one field, so a single inaccessible
 * organization can poison a whole window. On FORBIDDEN, bisect the window
 * until the inaccessible day(s) can be skipped while preserving all other
 * contributions.
 */
export async function fetchReposForWindow(login: string, from: Date, to: Date, out: Set<string>): Promise<void> {
	try {
		const data: WindowData = await ghRequest(windowQuery, {
			login,
			from: from.toISOString(),
			to: to.toISOString(),
		});
		const list = data.user?.contributionsCollection?.commitContributionsByRepository || [];
		for (const { repository } of list) {
			if (!repository?.nameWithOwner || isExcludedRepository(repository.nameWithOwner)) continue;
			out.add(repository.nameWithOwner);
		}

		console.log("fetched", list.length, "repos", "from", from.toISOString(), "to", to.toISOString());
		if (list.length < 100 || to.getTime() - from.getTime() <= 24 * 60 * 60 * 1000) return;
	} catch (error) {
		if (!isForbiddenError(error) || to.getTime() - from.getTime() <= 24 * 60 * 60 * 1000) {
			if (isForbiddenError(error)) {
				console.warn(`⚠️  Skipping inaccessible contribution window ${from.toISOString()} – ${to.toISOString()}.`);
				return;
			}
			throw error;
		}

		const midpoint = new Date((from.getTime() + to.getTime()) / 2);
		await fetchReposForWindow(login, from, midpoint, out);
		await fetchReposForWindow(login, midpoint, to, out);
		return;
	}

	// A full window with exactly 100 repositories may be truncated. Split it
	// even when the request itself succeeded so no repositories are lost.
	const midpoint = new Date((from.getTime() + to.getTime()) / 2);
	await fetchReposForWindow(login, from, midpoint, out);
	await fetchReposForWindow(login, midpoint, to, out);
}

export async function downloadAllRepos(): Promise<void> {
	if (!TOKEN || !LOGIN) {
		throw new Error("Usage: GH_TOKEN=token bun github/download.ts <github_login>");
	}

	// 1. Which years actually contain contributions?
	const yearsData: YearsData = await ghRequest(yearsQuery, { login: LOGIN });
	const years = yearsData.user.contributionsCollection.contributionYears;
	const userId = yearsData.user.id;
	if (!years.length) {
		console.log("No contributions found.");
		return;
	}

	const repos = new Set<string>();

	// 2. Discover every contribution year. A forbidden organization only makes
	// its own bisection branch inaccessible; all other windows remain usable.
	for (const year of years) {
		const from = new Date(`${year}-01-01T00:00:00.000Z`);
		const to = new Date(`${year + 1}-01-01T00:00:00.000Z`);
		await fetchReposForWindow(LOGIN, from, to, repos);
	}

	if (!repos.size) {
		throw new Error("No repositories found for the configured account.");
	}

	console.log("\n" + repos.size + " unique repositories with contributions by " + LOGIN + ":\n");
	console.log([...repos].sort().join("\n"));

	// Create progress bar for overall repository processing
	const overallProgressBar = new cliProgress.SingleBar({
		format: "Overall Progress |{bar}| {percentage}% | {value}/{total} repos | ETA: {eta}s | {repo}",
		barCompleteChar: "\u2588",
		barIncompleteChar: "\u2591",
		hideCursor: true,
	});

	overallProgressBar.start(repos.size, 0, { repo: "Starting..." });

	console.log("Fetching repository details and commits...");

	const allCommitsData: Record<string, GitHubCommit[]> = {};
	const allRepositoryDetails: Record<string, GitHubRepositoryDetails | null> = {};
	const failedRepos: Array<{ repo: string; error: string }> = [];

	const queue = new PQueue({
		concurrency: 5, // Reduced concurrency to avoid rate limits
		interval: 1000, // 1 second between requests
		intervalCap: 1, // Only 1 request per interval
	});

	let repoIndex = 0;
	await queue.addAll(
		[...repos.values()].map((repo) => async () => {
			const [owner, name] = repo.split("/");
			let commitProgressBar: cliProgress.SingleBar | null = null;

			try {
				const repoDetails = await fetchRepositoryDetails(owner, name);
				allRepositoryDetails[repo] = repoDetails;

				commitProgressBar = new cliProgress.SingleBar({
					format: `Commits for ${repo} |{bar}| {percentage}% | {value} refs | Current: {ref} | Commits: {totalCommits} | ETA: {eta}s`,
					barCompleteChar: "\u2588",
					barIncompleteChar: "\u2591",
					hideCursor: true,
				});

				commitProgressBar.start(1, 0, { ref: "Starting...", totalCommits: 0 });
				const commits = await fetchCommits(owner, name, userId, commitProgressBar);
				allCommitsData[repo] = commits;
			} catch (error) {
				const message = error instanceof Error ? error.message : String(error);
				failedRepos.push({ repo, error: message });
				delete allRepositoryDetails[repo];
				delete allCommitsData[repo];
			} finally {
				if (commitProgressBar) {
					commitProgressBar.stop();
				}
			}

			// Update overall progress
			repoIndex++;
			overallProgressBar.update(repoIndex, { repo });
		}),
	);

	// Complete overall progress bar
	overallProgressBar.stop();
	console.log("\nAll repositories processed. Total: " + repos.size);
	if (failedRepos.length) {
		console.log("\nWARN: Skipped " + failedRepos.length + " repositories due to errors:");
		failedRepos.forEach(({ repo, error }) => {
			console.log("- " + repo + ": " + error);
		});
	}

	const filteredRepos = Object.keys(allCommitsData).filter((repoName) => !isExcludedRepository(repoName));

	const outputData: GitHubExport = {
		repositories: Object.fromEntries(
			filteredRepos.map((repoName) => [
				repoName,
				{
					details: allRepositoryDetails[repoName] ?? null,
					commits: allCommitsData[repoName],
				},
			]),
		),
	};

	const timelineData = createGitHubTimelinePageData(outputData);
	const repositoryMetadata = createGitHubRepositoryMetadata(outputData);
	fs.writeFileSync(TIMELINE_OUTPUT_FILE, JSON.stringify(timelineData, null, 2) + "\n");
	fs.writeFileSync(REPOSITORIES_OUTPUT_FILE, JSON.stringify(repositoryMetadata, null, 2) + "\n");

	const totalCommits = filteredRepos.reduce((sum, repoName) => sum + allCommitsData[repoName].length, 0);
	const detailsCount = Object.values(allRepositoryDetails).filter((details) => details !== null).length;
	console.log("Saved timeline data to " + TIMELINE_OUTPUT_FILE);
	console.log("Saved repository metadata to " + REPOSITORIES_OUTPUT_FILE);
	console.log("Total commits: " + totalCommits);
	console.log("Repository details fetched: " + detailsCount);
}

const isMainModule = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isMainModule) {
	const args = process.argv.slice(2);

	if (args.includes("--help") || args.includes("-h")) {
		console.log(`
GitHub Repository Data Downloader

Usage:
GH_TOKEN=token bun github/download.ts [github_login]

Environment:
GITHUB_EXCLUDED_ORGS     Comma-separated organization logins to skip (ExodusMovement is skipped by default)
Output                   <script directory>/timeline.json and repositories.json
--help, -h             Show this help message

Examples:
bun github/download.ts                      # Refresh timeline and repository metadata
`);
	} else {
		void downloadAllRepos().catch((error: unknown) => {
			console.error(error);
			process.exitCode = 1;
		});
	}
}
