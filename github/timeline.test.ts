import { describe, expect, test } from "bun:test";
import {
	deduplicateRepositories,
	getEarliestContributionDate,
	groupProjectsByEarliestContributionYear,
	type TimelineRepository,
} from "./timeline";

function repository(
	overrides: Partial<TimelineRepository> & {
		details?: Partial<TimelineRepository["details"]>;
		commits?: TimelineRepository["commits"];
	},
): TimelineRepository {
	return {
		details: {
			id: "repository-id",
			nameWithOwner: "SamuelScheit/project",
			description: "A project that happens to mention 2030 in its description.",
			createdAt: "2020-01-01T00:00:00.000Z",
			isFork: false,
			owner: { login: "SamuelScheit" },
			...overrides.details,
		},
		commits: overrides.commits ?? [],
	};
}

describe("GitHub project timeline", () => {
	test("renders a multi-year project once under its earliest contribution year", () => {
		const longRunningProject = repository({
			commits: [
				{ oid: "2024", committedDate: "2024-11-20T18:00:00.000Z" },
				{ oid: "2022", committedDate: "2022-02-03T10:00:00.000Z" },
				{ oid: "2023", committedDate: "2023-01-01T00:00:00.000Z" },
			],
		});

		const groups = groupProjectsByEarliestContributionYear([longRunningProject]);

		expect(Object.keys(groups)).toEqual(["2022"]);
		expect(groups[2022].big).toEqual([longRunningProject]);
		expect(getEarliestContributionDate(longRunningProject).toISOString()).toBe("2022-02-03T10:00:00.000Z");
	});

	test("uses the complete project history for its size after choosing the first year", () => {
		const project = repository({
			commits: Array.from({ length: 11 }, (_, index) => ({
				oid: `${index}`,
				committedDate: index === 0 ? "2022-12-31T23:00:00.000Z" : "2023-01-02T00:00:00.000Z",
			})),
		});

		const groups = groupProjectsByEarliestContributionYear([project]);

		expect(groups[2022].big).toEqual([project]);
		expect(groups[2022].small).toEqual([]);
		expect(groups[2023]).toBeUndefined();
	});

	test("deduplicates renamed export entries by repository id using the earliest contribution", () => {
		const original = repository({
			details: { id: "stable-id", nameWithOwner: "SamuelScheit/old-name" },
			commits: [{ oid: "first", committedDate: "2021-06-01T00:00:00.000Z" }],
		});
		const renamed = repository({
			details: { id: "stable-id", nameWithOwner: "SamuelScheit/new-name" },
			commits: [
				{ oid: "first", committedDate: "2021-06-01T00:00:00.000Z" },
				{ oid: "later", committedDate: "2024-06-01T00:00:00.000Z" },
			],
		});

		const repositories = deduplicateRepositories([original, renamed]);
		const groups = groupProjectsByEarliestContributionYear([original, renamed]);

		expect(repositories).toHaveLength(1);
		expect(getEarliestContributionDate(repositories[0]).toISOString()).toBe("2021-06-01T00:00:00.000Z");
		expect(groups[2021].big).toHaveLength(1);
		expect(groups[2024]).toBeUndefined();
	});

	test("falls back to repository creation year only when contribution history is empty", () => {
		const projectWithoutCommits = repository({
			details: { createdAt: "2019-12-31T23:00:00.000Z" },
		});

		const groups = groupProjectsByEarliestContributionYear([projectWithoutCommits]);

		expect(groups[2019].big).toEqual([projectWithoutCommits]);
	});
});
