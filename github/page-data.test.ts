import { describe, expect, test } from "bun:test";
import {
	createGitHubRepositoryMetadata,
	createGitHubTimelinePageData,
	type GitHubExport,
	type GitHubRepositoryDetails,
} from "./page-data";

function repository(
	name: string,
	overrides: {
		details?: Partial<GitHubRepositoryDetails> & Record<string, unknown>;
		commits?: GitHubExport["repositories"][string]["commits"];
	} = {},
) {
	return {
		details: {
			id: name + "-id",
			name,
			nameWithOwner: "SamuelScheit/" + name,
			description: "A project",
			url: "https://github.com/SamuelScheit/" + name,
			homepageUrl: null,
			createdAt: "2024-01-01T00:00:00.000Z",
			isPrivate: false,
			isFork: false,
			forkCount: 0,
			stargazerCount: 0,
			primaryLanguage: null,
			owner: { login: "SamuelScheit" },
			openGraphImageUrl: null,
			...overrides.details,
		},
		commits: overrides.commits ?? [
			{
				oid: name + "-old",
				messageHeadline: "older commit",
				committedDate: "2024-01-02T00:00:00.000Z",
			},
			{
				oid: name + "-new",
				messageHeadline: "newer commit",
				committedDate: "2024-02-02T00:00:00.000Z",
			},
		],
	};
}

describe("GitHub page data", () => {
	test("keeps only rendered fields and uses newest commit previews", () => {
		const input = {
			repositories: {
				"SamuelScheit/project": repository("project", {
					details: {
						readme: { text: "This must never ship to the page." },
						pullRequests: [{ title: "private data" }],
					},
					commits: [
						{ oid: "1", messageHeadline: "oldest", committedDate: "2022-01-01T00:00:00.000Z", refs: ["main"] },
						{ oid: "2", messageHeadline: "newest", committedDate: "2024-01-01T00:00:00.000Z", refs: ["main"] },
					],
				}),
			},
		} as unknown as GitHubExport;

		const pageData = createGitHubTimelinePageData(input);
		const card = pageData.years[0].projects[0];

		expect(card.commitCount).toBe(2);
		expect(card.recentCommitMessages).toEqual(["newest", "oldest"]);
		expect(JSON.stringify(pageData)).not.toContain("This must never ship");
		expect(JSON.stringify(pageData)).not.toContain("pullRequests");
		expect(JSON.stringify(pageData)).not.toContain("refs");
	});

	test("aggregates excluded repositories by UTC commit year", () => {
		const input = {
			repositories: {
				"SamuelScheit/undocumented": repository("undocumented", {
					details: { description: "   " },
					commits: [
						{ oid: "a", messageHeadline: "a", committedDate: "2023-12-31T23:30:00.000Z" },
						{ oid: "b", messageHeadline: "b", committedDate: "2024-01-01T00:30:00.000Z" },
					],
				}),
			},
		} as unknown as GitHubExport;

		const pageData = createGitHubTimelinePageData(input);

		expect(pageData.years).toEqual([
			{
				year: 2024,
				projects: [],
				contributions: [],
				excludedRepositoryCount: 1,
				excludedCommitCount: 1,
			},
			{
				year: 2023,
				projects: [],
				contributions: [],
				excludedRepositoryCount: 1,
				excludedCommitCount: 1,
			},
		]);
	});

	test("strips raw repository fields from the CV metadata artifact", () => {
		const input = {
			repositories: {
				"SamuelScheit/project": repository("project", {
					details: {
						readme: { text: "private README" },
						languages: { edges: [] },
						pullRequests: [{ title: "private PR" }],
					},
				}),
			},
		} as unknown as GitHubExport;

		const metadata = createGitHubRepositoryMetadata(input);

		expect(metadata.repositories["SamuelScheit/project"]).toEqual({
			details: {
				name: "project",
				url: "https://github.com/SamuelScheit/project",
				isPrivate: false,
				isFork: false,
				owner: { login: "SamuelScheit" },
			},
		});
		expect(JSON.stringify(metadata)).not.toContain("private README");
		expect(JSON.stringify(metadata)).not.toContain("private PR");
	});
});
