import { GetStaticProps, InferGetStaticPropsType } from "next";
import { Timeline, TimelineItem } from "../../components/timeline";
import { format, parseISO } from "date-fns";
import { Links } from "../../components/Links";
import Link from "next/link";

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
}

interface Commit {
	oid: string;
	messageHeadline: string;
	committedDate: string;
	refs: string[];
}

interface Repository {
	details: RepositoryDetails;
	commits: Commit[];
	firstCommitDate?: Date;
}

interface GitHubData {
	user: string;
	totalRepositories: number;
	totalCommits: number;
	excludedRepositories?: Array<{
		nameWithOwner: string;
		owner: string;
		name: string;
		commits: Commit[];
		details: RepositoryDetails | null;
		pullRequests: any[];
	}>;
	excludedRepositoriesCount?: number;
	excludedRepositoriesCommits?: number;
	generatedAt: string;
	repositories: { [key: string]: Repository };
}

interface ProjectGroupByOrg {
	year: number;
	orgs: {
		[org: string]: {
			org: string;
			bigProjects: Repository[];
			smallProjects: Repository[];
		};
	};
}

// Array of repositories to exclude from the timeline

// Function to check if a repository should be excluded
function shouldExcludeRepo(repo: Repository): boolean {
	// Exclude if no description
	if (!repo.details.description || repo.details.description.trim() === "") {
		return true;
	}

	return false;
}

function categorizeProject(repo: Repository, year?: number): "big" | "small" {
	// Big projects: created by me OR if I committed more than 10 commits OR if it's a fork
	// Small projects: forked projects with minimal contributions

	const isOwnProject = repo.details.owner.login === "SamuelScheit";
	const isFork = repo.details.isFork;
	const commitCount = year ? getCommitsForYear(repo, year).length : repo.commits.length;

	if (isOwnProject) {
		return "big";
	}

	// If I committed more than 10 commits, it's a big project
	if (commitCount > 10) {
		return "big";
	}

	// If it's a fork, it's likely a small contribution
	if (isFork) {
		return "small";
	}

	return "small";
}

// Helper function to extract date from repository description
function extractDateFromDescription(description: string | null): Date | null {
	if (!description) return null;

	// Common date patterns in descriptions
	const datePatterns = [
		/(\d{4})/, // Just year
		/(\d{1,2})\/(\d{1,2})\/(\d{4})/, // MM/DD/YYYY or DD/MM/YYYY
		/(\d{4})-(\d{1,2})-(\d{1,2})/, // YYYY-MM-DD
		/(\d{1,2})-(\d{1,2})-(\d{4})/, // MM-DD-YYYY or DD-MM-YYYY
		/(\w+)\s+(\d{4})/, // Month Year (e.g., "January 2023")
		/(\d{4})\s+(\w+)/, // Year Month (e.g., "2023 January")
	];

	for (const pattern of datePatterns) {
		const match = description.match(pattern);
		if (match) {
			try {
				if (pattern.source === "(\\d{4})") {
					// Just year - create date for January 1st of that year
					return new Date(parseInt(match[1]), 0, 1);
				} else if (pattern.source === "(\\d{1,2})\\/(\\d{1,2})\\/(\\d{4})") {
					// MM/DD/YYYY or DD/MM/YYYY - assume MM/DD/YYYY for US format
					const month = parseInt(match[1]) - 1; // 0-indexed
					const day = parseInt(match[2]);
					const year = parseInt(match[3]);
					return new Date(year, month, day);
				} else if (pattern.source === "(\\d{4})-(\\d{1,2})-(\\d{1,2})") {
					// YYYY-MM-DD
					const year = parseInt(match[1]);
					const month = parseInt(match[2]) - 1; // 0-indexed
					const day = parseInt(match[3]);
					return new Date(year, month, day);
				} else if (pattern.source === "(\\d{1,2})-(\\d{1,2})-(\\d{4})") {
					// MM-DD-YYYY or DD-MM-YYYY - assume MM-DD-YYYY
					const month = parseInt(match[1]) - 1; // 0-indexed
					const day = parseInt(match[2]);
					const year = parseInt(match[3]);
					return new Date(year, month, day);
				} else if (pattern.source === "(\\w+)\\s+(\\d{4})") {
					// Month Year
					const monthName = match[1];
					const year = parseInt(match[2]);
					const monthIndex = new Date(`${monthName} 1, ${year}`).getMonth();
					return new Date(year, monthIndex, 1);
				} else if (pattern.source === "(\\d{4})\\s+(\\w+)") {
					// Year Month
					const year = parseInt(match[1]);
					const monthName = match[2];
					const monthIndex = new Date(`${monthName} 1, ${year}`).getMonth();
					return new Date(year, monthIndex, 1);
				}
			} catch (error) {
				// If date parsing fails, continue to next pattern
				continue;
			}
		}
	}

	return null;
}

// Helper function to get the first commit date for a repository
function getFirstCommitDate(repo: Repository): Date {
	// First, try to extract date from description
	const descriptionDate = extractDateFromDescription(repo.details.description);
	if (descriptionDate) {
		return descriptionDate;
	}

	// Fall back to first commit date
	if (repo.commits.length === 0) {
		// If no commits, fall back to repository creation date
		return parseISO(repo.details.createdAt);
	}

	// Get the earliest commit date
	const commitDates = repo.commits.map((commit) => parseISO(commit.committedDate));
	return new Date(Math.min(...commitDates.map((date) => date.getTime())));
}

// Add first commit date to repository objects for efficiency
function addFirstCommitDates(repos: { [key: string]: Repository }) {
	Object.values(repos).forEach((repo) => {
		repo.firstCommitDate = getFirstCommitDate(repo);
	});
}

// Helper function to get commits for a specific year
function getCommitsForYear(repo: Repository, year: number): Commit[] {
	return repo.commits.filter((commit) => {
		const commitDate = parseISO(commit.committedDate);
		return commitDate.getFullYear() === year;
	});
}

// Group repositories by year and organization
function groupReposByYearAndOrg(repos: { [key: string]: Repository }) {
	const yearGroups: { [year: number]: { [org: string]: Repository[] } } = {};

	Object.values(repos)
		.filter((repo) => !shouldExcludeRepo(repo))
		.forEach((repo) => {
			// Get all unique years from commits
			const commitYears = new Set<number>();

			// Add the first commit date year
			const firstCommitDate = repo.firstCommitDate!;
			commitYears.add(firstCommitDate.getFullYear());

			// Add years from all commits
			repo.commits.forEach((commit) => {
				const commitDate = parseISO(commit.committedDate);
				commitYears.add(commitDate.getFullYear());
			});

			commitYears.forEach((year) => {
				const commitsInYear = getCommitsForYear(repo, year).length;

				const org = repo.details.owner.login;

				if (!yearGroups[year]) {
					yearGroups[year] = {};
				}

				if (!yearGroups[year][org]) {
					yearGroups[year][org] = [];
				}

				// Check if this repo is already added for this year to avoid duplicates
				const existingRepo = yearGroups[year][org].find((r) => r.details.nameWithOwner === repo.details.nameWithOwner);
				if (!existingRepo) {
					yearGroups[year][org].push(repo);
				}
			});
		});

	// Sort repositories within each org by first commit date
	Object.keys(yearGroups).forEach((year) => {
		Object.keys(yearGroups[parseInt(year)]).forEach((org) => {
			yearGroups[parseInt(year)][org].sort((a, b) => {
				const aFirstCommit = a.firstCommitDate!;
				const bFirstCommit = b.firstCommitDate!;
				return bFirstCommit.getTime() - aFirstCommit.getTime();
			});
		});
	});

	return yearGroups;
}

// Separate big and small projects for each year
function separateProjectsBySize(repos: { [key: string]: Repository }) {
	const yearGroups = groupReposByYearAndOrg(repos);
	const result: { [year: number]: { big: Repository[]; small: Repository[] } } = {};

	Object.keys(yearGroups).forEach((yearStr) => {
		const year = parseInt(yearStr);
		const orgs = yearGroups[year];
		const bigProjects: Repository[] = [];
		const smallProjects: Repository[] = [];

		Object.values(orgs)
			.flat()
			.forEach((repo) => {
				if (categorizeProject(repo, year) === "big") {
					bigProjects.push(repo);
				} else {
					smallProjects.push(repo);
				}
			});

		result[year] = { big: bigProjects, small: smallProjects };
	});

	return result;
}

function getTopStarredProjects(repos: { [key: string]: Repository }) {
	const seenOrgs = new Set<string>();
	const topProjects: Repository[] = [];

	Object.values(repos)
		.filter((repo) => !repo.details.isFork && repo.commits.length > 30 && !shouldExcludeRepo(repo) && repo.details.stargazerCount > 100)
		.sort((a, b) => b.details.stargazerCount - a.details.stargazerCount)
		.forEach((repo) => {
			const org = repo.details.owner.login;
			if (org === "SamuelScheit" || !seenOrgs.has(org)) {
				topProjects.push(repo);
				if (org !== "SamuelScheit") seenOrgs.add(org);
			}
		});

	return topProjects;
}

export const getStaticProps = (async (context) => {
	// Import the data from the correct path
	const data: GitHubData = require("../../github/commits.json");

	// Pre-calculate first commit dates and convert to ISO strings for JSON serialization
	Object.values(data.repositories).forEach((repo) => {
		const firstCommitDate = getFirstCommitDate(repo);
		(repo as any).firstCommitDate = firstCommitDate.toISOString();
	});

	return { props: { data } };
}) satisfies GetStaticProps<{
	data: GitHubData;
}>;

export default function GitHubTimeline(props: InferGetStaticPropsType<typeof getStaticProps>) {
	const { data } = props;

	// Convert ISO strings back to Date objects for the component
	Object.values(data.repositories).forEach((repo) => {
		if ((repo as any).firstCommitDate) {
			(repo as any).firstCommitDate = new Date((repo as any).firstCommitDate);
		}
	});

	// Calculate excluded repositories locally
	const excludedRepos = Object.values(data.repositories).filter((repo) => shouldExcludeRepo(repo));

	const projectsByYear = separateProjectsBySize(data.repositories);
	const topProjects = getTopStarredProjects(data.repositories);

	// Sort years in descending order
	const sortedYears = Object.keys(projectsByYear)
		.map(Number)
		.sort((a, b) => b - a);

	return (
		<div className="main blog">
			<div className="links-wrapper">
				<Links>
					<Link href="/" title="Back" className="_absolute max-md:_hidden" style={{ left: "30px", top: "40px" }}>
						<svg xmlns="http://www.w3.org/2000/svg" width="2.3rem" height="2.3rem" viewBox="0 0 24 24">
							<path fill="currentColor" d="m15.914 17.5l-5.5-5.5l5.5-5.5L14.5 5.086L7.586 12l6.914 6.914z"></path>
						</svg>
					</Link>
				</Links>
			</div>
			<div style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem" }}>
				<div className="x:flex x:justify x:z-10 x:pb-10 x:justify-center">
					<Link
						href={"/"}
						className="x:text-center x:p-4 x:text-4xl x:font-bold x:bg-clip-text x:text-transparent!"
						style={{
							backgroundImage: "linear-gradient(90deg, rgba(0,124,240,1) 23%, rgba(0,223,216,1) 71%)",
							textDecoration: "none",
						}}
					>
						Samuel Scheit
					</Link>
				</div>

				<section style={{ margin: "0 auto 3rem auto", maxWidth: 1200, minHeight: "auto" }}>
					<h2
						style={{
							fontSize: "2.2rem",
							fontWeight: 700,
							textAlign: "center",
							marginBottom: "2rem",
							letterSpacing: "-1px",
						}}
					>
						Popular Projects
					</h2>
					<div style={{ display: "flex", gap: "2rem", justifyContent: "center", flexWrap: "wrap" }}>
						{topProjects.map((repo) => (
							<div key={repo.details.nameWithOwner} style={{ flex: "1 1 410px", maxWidth: 410 }}>
								<ProjectCard repo={repo} size="big" />
							</div>
						))}
					</div>
				</section>

				<Timeline style={{ marginBottom: "5rem", marginTop: "5rem" }}>
					{sortedYears.map((year) => {
						const { big: bigProjects, small: smallProjects } = projectsByYear[year];

						return (
							<TimelineItem key={year} date={year.toString()} title={`${year}`} titleStyle={{ color: "#ff7448" }}>
								<TimelineSection title="Projects" titleColor="#ff7448" show={bigProjects.length > 0}>
									<div
										style={{
											display: "grid",
											gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))",
											gap: "2rem",
										}}
									>
										{bigProjects.map((repo) => (
											<ProjectCard key={repo.details.nameWithOwner} repo={repo} size="big" year={year} />
										))}
									</div>
								</TimelineSection>

								<TimelineSection title="Contributions" titleColor="#6248ff" show={smallProjects.length > 0}>
									<div
										style={{
											display: "grid",
											gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
											gap: "1rem",
										}}
									>
										{smallProjects.map((repo) => (
											<SmallProjectCard key={repo.details.nameWithOwner} repo={repo} year={year} />
										))}
									</div>
								</TimelineSection>

								<TimelineSection title="">
									<ExcludedReposCard excludedRepos={excludedRepos} year={year} />
								</TimelineSection>
							</TimelineItem>
						);
					})}
				</Timeline>

				<div style={{ textAlign: "center", marginTop: "3rem", marginBottom: "2rem" }}>
					<Link
						href="/"
						style={{
							display: "inline-flex",
							alignItems: "center",
							gap: "0.5rem",
							padding: "0.75rem 1.5rem",
							background: "linear-gradient(135deg, rgba(98, 72, 255, 0.1) 0%, rgba(98, 72, 255, 0.2) 100%)",
							border: "1px solid rgba(98, 72, 255, 0.3)",
							borderRadius: "8px",
							color: "var(--text)",
							textDecoration: "none",
							fontWeight: "500",
							transition: "all 0.3s ease",
							cursor: "pointer",
						}}
						onMouseEnter={(e) => {
							e.currentTarget.style.transform = "translateY(-1px)";
							e.currentTarget.style.boxShadow = "0 4px 12px rgba(98, 72, 255, 0.2)";
						}}
						onMouseLeave={(e) => {
							e.currentTarget.style.transform = "translateY(0)";
							e.currentTarget.style.boxShadow = "none";
						}}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
							<path fill="currentColor" d="m15.914 17.5l-5.5-5.5l5.5-5.5L14.5 5.086L7.586 12l6.914 6.914z"></path>
						</svg>
						Go Back
					</Link>
				</div>
			</div>
		</div>
	);
}

function SmallProjectCard({ repo, year }: { repo: Repository; year: number }) {
	const linkUrl = repo.details.homepageUrl || repo.details.url;
	const isClickable = !repo.details.isPrivate || repo.details.homepageUrl;

	const cardStyle = {
		background: "linear-gradient(135deg, rgba(98, 72, 255, 0.05) 0%, rgba(98, 72, 255, 0.1) 100%)",
		border: "1px solid rgba(98, 72, 255, 0.2)",
		borderRadius: "8px",
		padding: "0.75rem",
		transition: "all 0.3s ease",
		position: "relative" as const,
		overflow: "hidden" as const,
		cursor: repo.details.isPrivate && !repo.details.homepageUrl ? ("default" as const) : ("pointer" as const),
		...(isClickable && {
			":hover": {
				transform: "translateY(-1px)",
				boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
			},
		}),
	};

	const cardContent = (
		<div style={cardStyle}>
			<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
				<div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: "0.5rem", flex: 1, minWidth: 0 }}>
					<h4
						style={{
							fontWeight: "600",
							fontSize: "0.9rem",
							color: "var(--text)",
							margin: 0,
							overflow: "hidden",
							textOverflow: "ellipsis",
							whiteSpace: "nowrap" as const,
						}}
					>
						{repo.details.name}
					</h4>
					<div
						style={{
							fontSize: "0.70rem",
							color: "var(--text-secondary)",
							fontWeight: 500,
							overflow: "hidden",
							textOverflow: "ellipsis",
							whiteSpace: "nowrap" as const,
						}}
					>
						{repo.details.owner.login}
					</div>
				</div>
				<div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
					{repo.details.isPrivate && !repo.details.homepageUrl && (
						<span
							style={{
								fontSize: "0.7rem",
								padding: "0.2rem 0.4rem",
								borderRadius: "8px",
								fontWeight: "500",
								background: "rgba(156, 163, 175, 0.1)",
								color: "rgb(156, 163, 175)",
							}}
						>
							Private
						</span>
					)}
					<span
						style={{
							fontSize: "0.7rem",
							padding: "0.2rem 0.4rem",
							borderRadius: "8px",
							fontWeight: "500",
							background: "rgba(98, 72, 255, 0.1)",
							color: "rgb(98, 72, 255)",
						}}
					>
						{getCommitsForYear(repo, year).length} commits
					</span>
				</div>
			</div>

			<div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginBottom: "0.5rem" }}>
				{getCommitsForYear(repo, year)
					.slice(0, 3)
					.map((commit, index) => (
						<div
							key={commit.oid}
							style={{
								marginBottom: "0.25rem",
								overflow: "hidden",
								textOverflow: "ellipsis",
								whiteSpace: "nowrap" as const,
							}}
						>
							• {commit.messageHeadline}
						</div>
					))}
				{getCommitsForYear(repo, year).length > 3 && (
					<div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", fontStyle: "italic" }}>
						+{getCommitsForYear(repo, year).length - 3} more commits
					</div>
				)}
			</div>
		</div>
	);

	return isClickable ? (
		<a
			href={linkUrl}
			target="_blank"
			rel="noopener noreferrer"
			style={{
				textDecoration: "none",
				color: "inherit",
				display: "block",
			}}
		>
			{cardContent}
		</a>
	) : (
		cardContent
	);
}

function ProjectCard({ repo, size, year }: { repo: Repository; size: "big" | "small"; year?: number }) {
	const isOwnProject = repo.details.owner.login === "SamuelScheit";
	const linkUrl = repo.details.homepageUrl || repo.details.url;
	const isClickable = !repo.details.isPrivate || repo.details.homepageUrl;

	const cardStyle = {
		background: "linear-gradient(135deg, rgba(98, 72, 255, 0.05) 0%, rgba(98, 72, 255, 0.1) 100%)",
		border: `1px solid rgba(98, 72, 255, 0.2)`,
		borderRadius: "12px",
		padding: "1.5rem",
		transition: "all 0.3s ease",
		position: "relative" as const,
		overflow: "hidden" as const,
		cursor: repo.details.isPrivate && !repo.details.homepageUrl ? ("default" as const) : ("pointer" as const),
		...(isClickable && {
			":hover": {
				transform: "translateY(-2px)",
				boxShadow: "0 8px 25px rgba(0, 0, 0, 0.1)",
			},
		}),
	};

	const cardContent = (
		<div style={cardStyle}>
			<div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "1rem" }}>
				<h3
					style={{
						fontWeight: "600",
						fontSize: "1.1rem",
						color: "var(--text)",
						margin: 0,
						flex: 1,
						overflow: "hidden",
						textOverflow: "ellipsis",
						whiteSpace: "nowrap" as const,
					}}
				>
					{repo.details.name}
					{repo.details.owner.login !== "SamuelScheit" && (
						<span
							style={{
								fontSize: "0.85em",
								color: "var(--text-secondary)",
								marginLeft: "0.5em",
								fontWeight: 400,
							}}
						>
							{repo.details.owner.login}
						</span>
					)}
				</h3>
				{repo.details.isPrivate && !repo.details.homepageUrl && (
					<span
						style={{
							fontSize: "0.75rem",
							padding: "0.25rem 0.5rem",
							borderRadius: "12px",
							marginLeft: "0.5rem",
							fontWeight: "500",
							background: "rgba(156, 163, 175, 0.1)",
							color: "rgb(156, 163, 175)",
						}}
					>
						Private
					</span>
				)}
				{repo.details.isFork && (
					<span
						style={{
							fontSize: "0.75rem",
							padding: "0.25rem 0.5rem",
							borderRadius: "12px",
							marginLeft: "0.5rem",
							fontWeight: "500",
							background: "rgba(156, 163, 175, 0.1)",
							color: "rgb(156, 163, 175)",
						}}
					>
						Fork
					</span>
				)}
			</div>

			{size === "big" &&
				repo.details.openGraphImageUrl &&
				repo.details.openGraphImageUrl.includes("repository-images.githubusercontent.com") && (
					<div
						style={{
							marginBottom: "1rem",
							width: "100%",
							height: "auto", // fixed height (2:1 aspect ratio)
							position: "relative",
							borderRadius: "8px",
							overflow: "hidden",
							border: "1px solid rgba(0, 0, 0, 0.1)",
						}}
					>
						<img
							src={repo.details.openGraphImageUrl}
							alt={`${repo.details.name} preview`}
							style={{
								width: "100%",
								height: "100%",
								objectFit: "cover",
								borderRadius: "8px",
								display: "block",
								top: 0,
								left: 0,
							}}
						/>
					</div>
				)}

			<p
				style={{
					fontSize: "0.9rem",
					color: "var(--text-secondary)",
					marginBottom: "1rem",
					lineHeight: "1.4",
					display: "-webkit-box",
					WebkitLineClamp: 2,
					WebkitBoxOrient: "vertical" as const,
					overflow: "hidden",
				}}
			>
				{repo.details.description || "No description"}
			</p>

			<div
				style={{
					display: "flex",
					alignItems: "center",
					justifyContent: "space-between",
					fontSize: "0.8rem",
					color: "var(--text-secondary)",
				}}
			>
				<div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
					{repo.details.primaryLanguage && (
						<>
							<div
								style={{
									width: "12px",
									height: "12px",
									borderRadius: "50%",
									flexShrink: 0,
									backgroundColor: repo.details.primaryLanguage.color,
								}}
							/>
							<span>{repo.details.primaryLanguage.name}</span>
						</>
					)}
				</div>

				<div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
					<span>⭐ {repo.details.stargazerCount}</span>
					<span>🍴 {repo.details.forkCount}</span>
				</div>
			</div>
		</div>
	);

	return isClickable ? (
		<a
			href={linkUrl}
			target="_blank"
			rel="noopener noreferrer"
			style={{
				textDecoration: "none",
				color: "inherit",
				display: "block",
			}}
		>
			{cardContent}
		</a>
	) : (
		cardContent
	);
}

function TimelineSection({
	title,
	titleColor,
	children,
	show = true,
}: {
	title: string;
	titleColor?: string;
	children: React.ReactNode;
	show?: boolean;
}) {
	if (!show) return null;

	return (
		<div style={{ marginBottom: "2rem" }}>
			<h3
				style={{
					fontSize: "1.5rem",
					fontWeight: "600",
					color: titleColor,
					marginBottom: "1rem",
				}}
			>
				{title}
			</h3>
			{children}
		</div>
	);
}

function ExcludedReposCard({ excludedRepos, year }: { excludedRepos: Repository[]; year: number }) {
	const yearExcludedRepos = excludedRepos.filter((repo) => {
		return repo.commits.some((commit) => {
			const commitDate = parseISO(commit.committedDate);
			return commitDate.getFullYear() === year;
		});
	});

	if (yearExcludedRepos.length === 0) return null;

	const totalCommits = yearExcludedRepos.reduce((sum, repo) => {
		const yearCommits = repo.commits.filter((commit) => {
			const commitDate = parseISO(commit.committedDate);
			return commitDate.getFullYear() === year;
		});
		return sum + yearCommits.length;
	}, 0);

	return (
		<div
			style={{
				background: "rgba(156, 163, 175, 0.08)",
				borderRadius: "10px",
				padding: "0.75rem 1.25rem",
				margin: "1.5rem 0 0.5rem 0",
				color: "var(--text-secondary)",
				fontSize: "1rem",
				textAlign: "center",
			}}
		>
			And {totalCommits} more commits in {yearExcludedRepos.length} other repositories.
		</div>
	);
}
