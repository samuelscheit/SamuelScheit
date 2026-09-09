import {
	deduplicateRepositories,
	groupProjectsByEarliestContributionYear,
	parseContributionDate,
	shouldExcludeRepository,
	type TimelineRepository,
} from "./timeline";

export interface GitHubCommit {
	oid: string;
	messageHeadline: string;
	committedDate: string;
}

export interface GitHubRepositoryDetails {
	id: string;
	name: string;
	nameWithOwner: string;
	description: string | null;
	url: string;
	homepageUrl: string | null;
	createdAt: string;
	isPrivate: boolean;
	isFork: boolean;
	forkCount: number;
	stargazerCount: number;
	primaryLanguage: {
		name: string;
		color: string;
	} | null;
	owner: {
		login: string;
	};
	openGraphImageUrl: string | null;
}

export interface GitHubRepository extends TimelineRepository {
	details: GitHubRepositoryDetails;
	commits: GitHubCommit[];
}

interface GitHubExportRepository {
	details: GitHubRepositoryDetails | null;
	commits: GitHubCommit[];
}

export interface GitHubExport {
	repositories: Record<string, GitHubExportRepository>;
}

export interface GitHubProjectCard {
	id: string;
	name: string;
	owner: string;
	description: string;
	url: string;
	homepageUrl: string | null;
	isPrivate: boolean;
	isFork: boolean;
	forkCount: number;
	stargazerCount: number;
	primaryLanguage: {
		name: string;
		color: string;
	} | null;
	openGraphImageUrl: string | null;
	commitCount: number;
	recentCommitMessages: string[];
}

export interface GitHubTimelineYear {
	year: number;
	projects: GitHubProjectCard[];
	contributions: GitHubProjectCard[];
	excludedRepositoryCount: number;
	excludedCommitCount: number;
}

export interface GitHubTimelinePageData {
	popularProjects: GitHubProjectCard[];
	years: GitHubTimelineYear[];
}

export interface GitHubRepositoryMetadata {
	details: Pick<GitHubRepositoryDetails, "name" | "url" | "isPrivate" | "isFork" | "owner">;
}

export interface GitHubRepositoryMetadataFile {
	repositories: Record<string, GitHubRepositoryMetadata>;
}

interface ExcludedContributions {
	repositoryIds: Set<string>;
	commitCount: number;
}

function hasDetails(repository: GitHubExportRepository): repository is GitHubRepository {
	return repository.details !== null;
}

function getRecentCommitMessages(commits: GitHubCommit[]): string[] {
	return [...commits]
		.sort((first, second) => {
			const firstTime = parseContributionDate(first.committedDate)?.getTime() ?? Number.MIN_SAFE_INTEGER;
			const secondTime = parseContributionDate(second.committedDate)?.getTime() ?? Number.MIN_SAFE_INTEGER;

			return secondTime - firstTime || first.oid.localeCompare(second.oid);
		})
		.slice(0, 3)
		.map((commit) => commit.messageHeadline);
}

function createProjectCardFactory() {
	const cardsByRepositoryId = new Map<string, GitHubProjectCard>();

	return (repository: GitHubRepository): GitHubProjectCard => {
		const existingCard = cardsByRepositoryId.get(repository.details.id);
		if (existingCard) return existingCard;

		const card: GitHubProjectCard = {
			id: repository.details.id,
			name: repository.details.name,
			owner: repository.details.owner.login,
			description: repository.details.description ?? "",
			url: repository.details.url,
			homepageUrl: repository.details.homepageUrl,
			isPrivate: repository.details.isPrivate,
			isFork: repository.details.isFork,
			forkCount: repository.details.forkCount,
			stargazerCount: repository.details.stargazerCount,
			primaryLanguage: repository.details.primaryLanguage,
			openGraphImageUrl: repository.details.openGraphImageUrl,
			commitCount: repository.commits.length,
			recentCommitMessages: getRecentCommitMessages(repository.commits),
		};

		cardsByRepositoryId.set(repository.details.id, card);
		return card;
	};
}

function getPopularProjects(repositories: GitHubRepository[]): GitHubRepository[] {
	const seenOrganizations = new Set<string>();
	const popularProjects: GitHubRepository[] = [];

	repositories
		.filter(
			(repository) =>
				!repository.details.isFork &&
				repository.commits.length > 30 &&
				!shouldExcludeRepository(repository) &&
				repository.details.stargazerCount > 100,
		)
		.sort((first, second) => second.details.stargazerCount - first.details.stargazerCount)
		.forEach((repository) => {
			const organization = repository.details.owner.login;
			if (organization === "SamuelScheit" || !seenOrganizations.has(organization)) {
				popularProjects.push(repository);
				if (organization !== "SamuelScheit") seenOrganizations.add(organization);
			}
		});

	return popularProjects;
}

function getExcludedContributionsByYear(repositories: GitHubRepository[]): Map<number, ExcludedContributions> {
	const contributionsByYear = new Map<number, ExcludedContributions>();

	for (const repository of repositories) {
		if (!shouldExcludeRepository(repository)) continue;

		for (const commit of repository.commits) {
			const year = parseContributionDate(commit.committedDate)?.getUTCFullYear();
			if (year === undefined) continue;

			const contributions = contributionsByYear.get(year) ?? { repositoryIds: new Set<string>(), commitCount: 0 };
			contributions.repositoryIds.add(repository.details.id);
			contributions.commitCount += 1;
			contributionsByYear.set(year, contributions);
		}
	}

	return contributionsByYear;
}

/**
 * Reduces the complete GitHub export to the exact static data required by the
 * timeline. This deliberately keeps raw commit histories, refs, README files,
 * and pull requests out of Next.js page props, where they would otherwise be
 * duplicated into both the rendered document and __NEXT_DATA__.
 */
export function createGitHubTimelinePageData(exportData: GitHubExport): GitHubTimelinePageData {
	const repositories = deduplicateRepositories(Object.values(exportData.repositories).filter(hasDetails));
	const projectsByYear = groupProjectsByEarliestContributionYear(repositories);
	const excludedContributionsByYear = getExcludedContributionsByYear(repositories);
	const toProjectCard = createProjectCardFactory();
	const years = new Set([
		...Object.keys(projectsByYear).map(Number),
		...excludedContributionsByYear.keys(),
	]);

	return {
		popularProjects: getPopularProjects(repositories).map(toProjectCard),
		years: [...years]
			.sort((first, second) => second - first)
			.map((year) => {
				const projects = projectsByYear[year] ?? { big: [], small: [] };
				const excludedContributions = excludedContributionsByYear.get(year);

				return {
					year,
					projects: projects.big.map(toProjectCard),
					contributions: projects.small.map(toProjectCard),
					excludedRepositoryCount: excludedContributions?.repositoryIds.size ?? 0,
					excludedCommitCount: excludedContributions?.commitCount ?? 0,
				};
			}),
	};
}

/**
 * Keeps the small repository metadata file used by the CV builder separate
 * from the timeline payload sent to browsers.
 */
export function createGitHubRepositoryMetadata(exportData: GitHubExport): GitHubRepositoryMetadataFile {
	const repositories: Record<string, GitHubRepositoryMetadata> = {};

	for (const [repositoryKey, repository] of Object.entries(exportData.repositories)) {
		if (repository.details) {
			repositories[repositoryKey] = {
				details: {
					name: repository.details.name,
					url: repository.details.url,
					isPrivate: repository.details.isPrivate,
					isFork: repository.details.isFork,
					owner: { login: repository.details.owner.login },
				},
			};
		}
	}

	return { repositories };
}
