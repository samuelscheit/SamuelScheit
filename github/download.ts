// file: contributed-repos.js
import fetch from "node-fetch";
import { parseISO, addDays, addYears, isAfter } from "date-fns";
import { config } from "dotenv";
import cliProgress from "cli-progress";
import PQueue from "p-queue";

config();

const TOKEN = process.env.GH_TOKEN;
const LOGIN = "samuelscheit";

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

// TypeScript interfaces for GraphQL responses
interface Repository {
	nameWithOwner: string;
}

interface RepositoryDetails {
	id: string;
	name: string;
	nameWithOwner: string;
	description: string | null;
	url: string;
	homepageUrl: string | null;
	createdAt: string;
	updatedAt: string;
	pushedAt: string;
	isPrivate: boolean;
	isFork: boolean;
	isArchived: boolean;
	isDisabled: boolean;
	isTemplate: boolean;
	isLocked: boolean;
	hasIssuesEnabled: boolean;
	hasWikiEnabled: boolean;
	hasDiscussionsEnabled: boolean;
	forkCount: number;
	stargazerCount: number;
	watchers: {
		totalCount: number;
	};
	primaryLanguage: {
		name: string;
		color: string;
	} | null;
	languages: {
		edges: Array<{
			size: number;
			node: {
				name: string;
				color: string;
			};
		}>;
	};
	licenseInfo: {
		name: string;
		spdxId: string;
		url: string;
	} | null;
	owner: {
		login: string;
		avatarUrl: string;
	};
	repositoryTopics: {
		nodes: Array<{
			topic: {
				name: string;
			};
		}>;
	};
	defaultBranchRef: {
		name: string;
		target: {
			history: {
				totalCount: number;
			};
		} | null;
	} | null;
	openGraphImageUrl: string | null;
	readme: {
		text: string;
	} | null;
	pullRequests: {
		totalCount: number;
		nodes: Array<{
			id: string;
			title: string;
			url: string;
			state: string;
			createdAt: string;
			updatedAt: string;
			closedAt: string | null;
			mergedAt: string | null;
			number: number;
			body: string | null;
			headRefName: string;
			baseRefName: string;
			author: {
				login: string;
			} | null;
		}>;
	};
}

interface CommitContribution {
	repository: Repository;
}

interface ContributionsCollection {
	commitContributionsByRepository: CommitContribution[];
}

interface User {
	contributionsCollection: ContributionsCollection;
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
	user: User;
}

interface GraphQLResponse<T> {
	data: T;
	errors?: any[];
}

// Function parameter and return types
interface GhRequestParams {
	query: string;
	variables: Record<string, any>;
}

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
  query ($owner: String!, $name: String!, $searchQuery: String!) {
    repository(owner: $owner, name: $name) {
      id
      name
      nameWithOwner
      description
      url
      homepageUrl
      createdAt
      updatedAt
      pushedAt
      isPrivate
      isFork
      isArchived
      isDisabled
      isTemplate
      isLocked
      hasIssuesEnabled
      hasWikiEnabled
      hasDiscussionsEnabled
      forkCount
      stargazerCount
      watchers {
        totalCount
      }
      primaryLanguage {
        name
        color
      }
      languages(first: 10) {
        edges {
          size
          node {
            name
            color
          }
        }
      }
      licenseInfo {
        name
        spdxId
        url
      }
      owner {
        login
        avatarUrl
      }
      repositoryTopics(first: 20) {
        nodes {
          topic {
            name
          }
        }
      }
      defaultBranchRef {
        name
        target {
          ... on Commit {
            history {
              totalCount
            }
          }
        }
      }
      openGraphImageUrl
      readme: object(expression: "HEAD:README.md") {
        ... on Blob {
          text
        }
      }
    }
    pullRequests: search(type: ISSUE, first: 100, query: $searchQuery) {
      nodes {
        ... on PullRequest {
          id
          title
          url
          state
          createdAt
          updatedAt
          closedAt
          mergedAt
          number
          body
          headRefName
          baseRefName
          author {
            login
          }
        }
      }
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
			if (attempt === retries - 1) {
				console.log(`❌ Request failed, no more retries (${attemptLabel})`, message, query, variables);
				throw error;
			}
			console.log(`⚠️  Request failed, retrying in 5 seconds... (${attemptLabel})`, message, query, variables);
			await new Promise((resolve) => setTimeout(resolve, 5000));
		}
	}
}

export async function fetchRepositoryDetails(
	owner: string,
	name: string,
	author: string,
): Promise<{ details: RepositoryDetails | null; pullRequests: any[] }> {
	try {
		const searchQuery = `repo:${owner}/${name} type:pr author:${author}`;
		const data = await ghRequest(repositoryDetailsQuery, { owner, name, searchQuery });
		return {
			details: data.repository,
			pullRequests: data.pullRequests?.nodes || [],
		};
	} catch (error) {
		console.log(`⚠️  Failed to fetch repository details for ${owner}/${name}:`, error);
		return {
			details: null,
			pullRequests: [],
		};
	}
}

export async function fetchCommits(owner: string, name: string, authorId: string, progressBar?: cliProgress.SingleBar) {
	const commitsMap = new Map<
		string,
		{
			oid: string;
			messageHeadline: string;
			committedDate: string;
			refs: string[];
		}
	>();

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
					if (commitsMap.has(oid)) {
						// Commit already exists, just add the ref if it's not already there
						const existing = commitsMap.get(oid)!;
						if (!existing.refs.includes(refName)) {
							existing.refs.push(refName);
						}
					} else {
						// New commit, add it to the map
						commitsMap.set(oid, {
							oid,
							messageHeadline,
							committedDate,
							refs: [refName],
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

	// Convert map to array format
	return Array.from(commitsMap.values()).map((commit) => ({
		oid: commit.oid,
		messageHeadline: commit.messageHeadline,
		committedDate: commit.committedDate,
		refs: commit.refs,
	}));
}

export async function fetchReposForWindow(login: string, from: Date, to: Date, out: Set<string>): Promise<void> {
	const vars = { login, from: from.toISOString(), to: to.toISOString() };
	const data: WindowData = await ghRequest(windowQuery, vars);
	const list = data.user.contributionsCollection.commitContributionsByRepository;
	list.forEach(({ repository }) => out.add(repository.nameWithOwner));

	console.log("fetched", list.length, "repos", "from", from, "to", to);

	// Only split if exactly 100 repos returned (indicating pagination limit)
	if (list.length === 100 && isAfter(to, addDays(from, 1))) {
		const mid = new Date((from.getTime() + to.getTime()) / 2);
		await fetchReposForWindow(login, from, mid, out);
		await fetchReposForWindow(login, addDays(mid, 1), to, out);
	}
}

export async function downloadAllRepos(
	options: {
		updateDetailsOnly?: boolean;
		skipRepoDiscovery?: boolean;
	} = {},
): Promise<void> {
	if (!TOKEN || !LOGIN) {
		console.error("Usage: GH_TOKEN=token node contributed-repos.js <github_login>");
		process.exit(1);
	}

	// 1. Which years actually contain contributions?
	const yearsData: YearsData = await ghRequest(yearsQuery, { login: LOGIN });
	const years = yearsData.user.contributionsCollection.contributionYears;
	const userId = yearsData.user.id;
	if (!years.length) return console.log("No contributions found.");

	const repos = new Set<string>();

	// 2. Walk each year and slice as needed (skip if skipRepoDiscovery is true)
	if (!options.skipRepoDiscovery) {
		for (const y of years) {
			const yearStart = parseISO(`${y}-01-01T00:00:00Z`);
			const yearEnd = addYears(yearStart, 1);
			await fetchReposForWindow(LOGIN, yearStart, yearEnd, repos);
		}
	}

	// Handle updateDetailsOnly mode
	if (options.updateDetailsOnly) {
		const fs = require("fs");
		const outputFile = "commits.json";

		// Check if commits.json exists
		if (!fs.existsSync(outputFile)) {
			console.error(`❌ File ${outputFile} not found. Please run the full download first.`);
			process.exit(1);
		}

		// Load existing data
		console.log(`📖 Loading existing data from ${outputFile}...`);
		const existingData = JSON.parse(fs.readFileSync(outputFile, "utf8"));
		const existingRepos = Object.keys(existingData.repositories);

		existingRepos.forEach((repo) => repos.add(repo));

		console.log(`🔄 Updating repository details for ${repos.size} repositories...`);
	} else {
		// 3. Output
		console.log(`\n${repos.size} unique repositories with commits by ${LOGIN}:\n`);
		console.log([...repos].sort().join("\n"));
	}

	// Create progress bar for overall repository processing
	const overallProgressBar = new cliProgress.SingleBar({
		format: "Overall Progress |{bar}| {percentage}% | {value}/{total} repos | ETA: {eta}s | {repo}",
		barCompleteChar: "\u2588",
		barIncompleteChar: "\u2591",
		hideCursor: true,
	});

	overallProgressBar.start(repos.size, 0, { repo: "Starting..." });

	if (options.updateDetailsOnly) {
		console.log("🔍 Fetching updated repository details and pull requests for all repositories...");
	} else {
		console.log("🔍 Fetching repository details, commits, and pull requests for all repositories...");
	}

	// Collect all commit data, repository details, and pull requests
	const allCommitsData: Record<string, any[]> = {};
	const allRepositoryDetails: Record<string, RepositoryDetails | null> = {};
	const allPullRequestsData: Record<string, any[]> = {};
	const failedRepos: Array<{ repo: string; error: string }> = [];

	// Load existing data if updating details only
	let existingData: any = null;
	if (options.updateDetailsOnly) {
		const fs = require("fs");
		const outputFile = "commits.json";
		existingData = JSON.parse(fs.readFileSync(outputFile, "utf8"));
	}

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
				// Fetch repository details and pull requests together
				const { details: repoDetails, pullRequests } = await fetchRepositoryDetails(owner, name, LOGIN);
				allRepositoryDetails[repo] = repoDetails;
				allPullRequestsData[repo] = pullRequests;

				// Skip commits if updating details only
				if (!options.updateDetailsOnly) {
					// Create individual progress bar for commits in this repo
					commitProgressBar = new cliProgress.SingleBar({
						format: `Commits for ${repo} |{bar}| {percentage}% | {value} refs | Current: {ref} | Commits: {totalCommits} | ETA: {eta}s`,
						barCompleteChar: "\u2588",
						barIncompleteChar: "\u2591",
						hideCursor: true,
					});

					commitProgressBar.start(1, 0, { ref: "Starting...", totalCommits: 0 }); // Will be updated with actual ref count

					const commits = await fetchCommits(owner, name, userId, commitProgressBar);

					// Store commits data for this repository
					allCommitsData[repo] = commits;
				} else {
					// Use existing commits data
					allCommitsData[repo] = existingData.repositories[repo].commits;
				}
			} catch (error) {
				const message = error instanceof Error ? error.message : String(error);
				failedRepos.push({ repo, error: message });
				delete allRepositoryDetails[repo];
				delete allPullRequestsData[repo];
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
	console.log(`\n🎉 All repositories processed! Total: ${repos.size} repositories`);
	if (failedRepos.length) {
		console.log(`\nWARN: Skipped ${failedRepos.length} repositories due to errors:`);
		failedRepos.forEach(({ repo, error }) => {
			console.log(`- ${repo}: ${error}`);
		});
	}

	// Save all commit data, repository details, and pull requests to file
	const fs = require("fs");

	// Filter out excluded repositories
	const filteredRepos = Object.keys(allCommitsData).filter((repoName) => !EXCLUDED_REPOS.includes(repoName));

	const outputData = {
		user: LOGIN,
		totalRepositories: filteredRepos.length,
		totalCommits: filteredRepos.reduce((sum, repoName) => sum + allCommitsData[repoName].length, 0),
		totalPullRequests: filteredRepos.reduce((sum, repoName) => sum + (allPullRequestsData[repoName] || []).length, 0),
		generatedAt: new Date().toISOString(),
		repositories: filteredRepos.reduce(
			(acc, repoName) => {
				acc[repoName] = {
					details: allRepositoryDetails[repoName],
					commits: allCommitsData[repoName],
					pullRequests: allPullRequestsData[repoName] || [],
				};
				return acc;
			},
			{} as Record<string, { details: RepositoryDetails | null; commits: any[]; pullRequests: any[] }>,
		),
	};

	const outputFile = `commits.json`;
	fs.writeFileSync(outputFile, JSON.stringify(outputData, null, 2));
	console.log(`\n💾 Commit data, repository details, and pull requests saved to: ${outputFile}`);
	console.log(`📊 Total commits across all repositories: ${outputData.totalCommits}`);
	console.log(`📊 Total pull requests across all repositories: ${outputData.totalPullRequests}`);
	console.log(
		`📋 Repository details fetched for ${Object.values(allRepositoryDetails).filter((details) => details !== null).length} repositories`,
	);
}

const args = process.argv.slice(2);

if (args.includes("--help") || args.includes("-h")) {
	console.log(`
GitHub Repository Data Downloader

Usage:
node github/download.ts [options]

Options:
--update-details, -u    Update only repository details (keep existing commit data)
--skip-discovery, -s    Skip repository discovery, use hardcoded list
--help, -h             Show this help message

Examples:
node github/download.ts                    # Full download (commits + details)
node github/download.ts --update-details   # Update only repository details
node github/download.ts -u                 # Short form for update details
node github/download.ts --skip-discovery   # Skip repo discovery, use hardcoded list
`);
} else {
	downloadAllRepos({
		updateDetailsOnly: args.includes("--update-details") || args.includes("-u"),
		skipRepoDiscovery: args.includes("--skip-discovery") || args.includes("-s"),
	});
}
