import type { GetStaticProps, InferGetStaticPropsType } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { Links } from "../../components/Links";
import { Timeline, TimelineItem } from "../../components/timeline";
import timelineData from "../../github/timeline.json";
import {
	type GitHubProjectCard,
	type GitHubTimelinePageData,
} from "../../github/page-data";

export const getStaticProps = (() => {
	return { props: { data: timelineData as GitHubTimelinePageData } };
}) satisfies GetStaticProps<{ data: GitHubTimelinePageData }>;

export default function GitHubTimeline({ data }: InferGetStaticPropsType<typeof getStaticProps>) {
	return (
		<div className="main blog">
			<div className="links-wrapper">
				<Links>
					<Link href="/" title="Back" className="_absolute max-md:_hidden" style={{ left: "30px", top: "40px" }}>
						<BackIcon size="2.3rem" />
					</Link>
				</Links>
			</div>

			<main className="github-timeline">
				<h1 className="github-timeline__title">
					<Link href="/">Samuel Scheit</Link>
				</h1>

				{data.popularProjects.length > 0 && (
					<div className="github-timeline__popular">
						<h2>Popular Projects</h2>
						<div className="github-timeline__popular-grid">
							{data.popularProjects.map((project) => (
								<ProjectCard key={project.id} project={project} />
							))}
						</div>
					</div>
				)}

				<Timeline className="github-timeline__timeline">
					{data.years.map((timelineYear) => (
						<TimelineItem key={timelineYear.year} date={timelineYear.year.toString()}>
							<TimelineSection title="Projects" titleColor="#ff7448" show={timelineYear.projects.length > 0}>
								<div className="github-timeline__project-grid">
									{timelineYear.projects.map((project) => (
										<ProjectCard key={project.id} project={project} />
									))}
								</div>
							</TimelineSection>

							<TimelineSection
								title="Contributions"
								titleColor="#6248ff"
								show={timelineYear.contributions.length > 0}
							>
								<div className="github-timeline__contribution-grid">
									{timelineYear.contributions.map((project) => (
										<ContributionCard key={project.id} project={project} />
									))}
								</div>
							</TimelineSection>

							{timelineYear.excludedRepositoryCount > 0 && (
								<div className="github-timeline__excluded">
									And {timelineYear.excludedCommitCount} more commits in {timelineYear.excludedRepositoryCount} other{" "}
									{timelineYear.excludedRepositoryCount === 1 ? "repository" : "repositories"} in {timelineYear.year}.
								</div>
							)}
						</TimelineItem>
					))}
				</Timeline>

				<div className="github-timeline__back">
					<Link href="/" className="github-timeline__back-link">
						<BackIcon size="16" />
						Go Back
					</Link>
				</div>
			</main>
		</div>
	);
}

function ProjectCard({ project }: { project: GitHubProjectCard }) {
	return (
		<ProjectLink project={project}>
			<article className="github-project-card">
				<div className="github-project-card__header">
					<h3 className="github-project-card__name">
						{project.name}
						{project.owner !== "SamuelScheit" && (
							<span className="github-project-card__owner">{project.owner}</span>
						)}
					</h3>
					<ProjectBadges project={project} />
				</div>

				{project.openGraphImageUrl?.includes("repository-images.githubusercontent.com") && (
					<div className="github-project-card__preview">
						<img
							src={project.openGraphImageUrl}
							alt={project.name + " preview"}
							loading="lazy"
							decoding="async"
						/>
					</div>
				)}

				<p className="github-project-card__description">{project.description}</p>
				<ProjectStats project={project} />
			</article>
		</ProjectLink>
	);
}

function ContributionCard({ project }: { project: GitHubProjectCard }) {
	return (
		<ProjectLink project={project}>
			<article className="github-contribution-card">
				<div className="github-contribution-card__header">
					<div className="github-contribution-card__title">
						<h3>{project.name}</h3>
						<span>{project.owner}</span>
					</div>
					<ProjectBadges project={project} compact />
					<span className="github-contribution-card__count">{project.commitCount} commits</span>
				</div>

				<div className="github-contribution-card__messages">
					{project.recentCommitMessages.map((message, index) => (
						<div key={project.id + "-" + index}>• {message}</div>
					))}
					{project.commitCount > project.recentCommitMessages.length && (
						<div className="github-contribution-card__more">
							+{project.commitCount - project.recentCommitMessages.length} more commits
						</div>
					)}
				</div>
			</article>
		</ProjectLink>
	);
}

function ProjectLink({ project, children }: { project: GitHubProjectCard; children: ReactNode }) {
	const href = project.homepageUrl || project.url;
	const isClickable = !project.isPrivate || Boolean(project.homepageUrl);

	if (!isClickable) return children;

	return (
		<a className="github-timeline__card-link" href={href} target="_blank" rel="noopener noreferrer">
			{children}
		</a>
	);
}

function ProjectBadges({ project, compact = false }: { project: GitHubProjectCard; compact?: boolean }) {
	const isPrivateWithoutHomepage = project.isPrivate && !project.homepageUrl;

	if (!isPrivateWithoutHomepage && !project.isFork) return null;

	return (
		<div className={compact ? "github-project-badges github-project-badges--compact" : "github-project-badges"}>
			{isPrivateWithoutHomepage && <span>Private</span>}
			{project.isFork && <span>Fork</span>}
		</div>
	);
}

function ProjectStats({ project }: { project: GitHubProjectCard }) {
	return (
		<div className="github-project-card__stats">
			<div className="github-project-card__language">
				{project.primaryLanguage && (
					<>
						<span
							className="github-project-card__language-dot"
							style={{ backgroundColor: project.primaryLanguage.color }}
						/>
						<span>{project.primaryLanguage.name}</span>
					</>
				)}
			</div>
			<div className="github-project-card__repository-stats">
				<span>⭐ {project.stargazerCount}</span>
				<span>🍴 {project.forkCount}</span>
			</div>
		</div>
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
	children: ReactNode;
	show?: boolean;
}) {
	if (!show) return null;

	return (
		<div className="github-timeline__section">
			<h2 style={{ color: titleColor }}>{title}</h2>
			{children}
		</div>
	);
}

function BackIcon({ size }: { size: string }) {
	return (
		<svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
			<path fill="currentColor" d="m15.914 17.5l-5.5-5.5l5.5-5.5L14.5 5.086L7.586 12l6.914 6.914z" />
		</svg>
	);
}
