export interface TimelineCommit {
	oid: string;
	committedDate: string;
}

export interface TimelineRepository {
	details: {
		id: string;
		nameWithOwner: string;
		description: string | null;
		createdAt: string;
		isFork: boolean;
		owner: {
			login: string;
		};
	};
	commits: TimelineCommit[];
}

export type ProjectSize = "big" | "small";

export type ProjectsByYear<TRepository extends TimelineRepository> = Record<
	number,
	{
		big: TRepository[];
		small: TRepository[];
	}
>;

function parseDate(value: string): Date | null {
	const date = new Date(value);
	return Number.isNaN(date.getTime()) ? null : date;
}

function compareRepositories<TRepository extends TimelineRepository>(a: TRepository, b: TRepository): number {
	const dateDifference = getEarliestContributionDate(a).getTime() - getEarliestContributionDate(b).getTime();
	if (dateDifference !== 0) return dateDifference;

	return a.details.nameWithOwner.localeCompare(b.details.nameWithOwner);
}

/**
 * Excludes repositories that cannot be presented as a project card.
 */
export function shouldExcludeRepository(repository: TimelineRepository): boolean {
	return !repository.details.description?.trim();
}

/**
 * Uses the user's earliest attributed commit. A repository's creation date is
 * only a fallback for repositories without commit history in the export.
 */
export function getEarliestContributionDate(repository: TimelineRepository): Date {
	const commitDates = repository.commits
		.map((commit) => parseDate(commit.committedDate))
		.filter((date): date is Date => date !== null);

	if (commitDates.length > 0) {
		return new Date(Math.min(...commitDates.map((date) => date.getTime())));
	}

	const createdAt = parseDate(repository.details.createdAt);
	if (!createdAt) {
		throw new Error(`Repository ${repository.details.nameWithOwner} has no valid contribution or creation date.`);
	}

	return createdAt;
}

/**
 * A GitHub repository has one canonical timeline entry. The export is keyed
 * by repository name, which can change, so deduplicate by GitHub's stable id.
 * Duplicate entries are impossible in current exports; should stale data
 * contain them, choose the entry with the earliest contribution deterministically.
 */
export function deduplicateRepositories<TRepository extends TimelineRepository>(
	repositories: Iterable<TRepository>,
): TRepository[] {
	const repositoriesById = new Map<string, TRepository>();

	for (const repository of repositories) {
		const existing = repositoriesById.get(repository.details.id);
		if (!existing || compareRepositories(repository, existing) < 0) {
			repositoriesById.set(repository.details.id, repository);
		}
	}

	return [...repositoriesById.values()];
}

export function categorizeProject(repository: TimelineRepository): ProjectSize {
	return repository.details.owner.login === "SamuelScheit" || repository.commits.length > 10 ? "big" : "small";
}

/**
 * Groups every repository exactly once: under the UTC year of its earliest
 * attributed commit. UTC avoids a repository at midnight on 1 January moving
 * into the prior year during client-side rendering in a negative time zone.
 */
export function groupProjectsByEarliestContributionYear<TRepository extends TimelineRepository>(
	repositories: Iterable<TRepository>,
): ProjectsByYear<TRepository> {
	const groups: ProjectsByYear<TRepository> = {};

	for (const repository of deduplicateRepositories(repositories)) {
		if (shouldExcludeRepository(repository)) continue;

		const year = getEarliestContributionDate(repository).getUTCFullYear();
		const size = categorizeProject(repository);
		(groups[year] ??= { big: [], small: [] })[size].push(repository);
	}

	for (const group of Object.values(groups)) {
		group.big.sort(compareRepositories);
		group.small.sort(compareRepositories);
	}

	return groups;
}
