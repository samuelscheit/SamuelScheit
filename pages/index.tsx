import Head from "next/head";
import type { GetStaticProps, InferGetStaticPropsType } from "next";
import { promises as fs } from "node:fs";
import path from "node:path";
import { About } from "../components/about";
import { BlogPosts, type BlogPost } from "../components/blog";
import { Contact } from "../components/contact";
import { Hero } from "../components/hero";
import { Links } from "../components/Links";
import { Projects } from "../components/projects";

function parseFrontMatter(source: string): Record<string, string> {
	const match = source.match(/^---\n([\s\S]*?)\n---/);
	if (!match) return {};

	return match[1]
		.split("\n")
		.map((line) => line.trim())
		.filter(Boolean)
		.reduce<Record<string, string>>((acc, line) => {
			const separatorIndex = line.indexOf(":");
			if (separatorIndex === -1) return acc;
			const key = line.slice(0, separatorIndex).trim();
			const value = line.slice(separatorIndex + 1).trim();
			acc[key] = value;
			return acc;
		}, {});
}

async function collectMdxFiles(dir: string): Promise<string[]> {
	const entries = await fs.readdir(dir, { withFileTypes: true });
	const files = await Promise.all(
		entries.map(async (entry) => {
			const fullPath = path.join(dir, entry.name);
			if (entry.isDirectory()) {
				return collectMdxFiles(fullPath);
			}
			return entry.name.endsWith(".mdx") ? [fullPath] : [];
		}),
	);
	return files.flat();
}

async function getBlogPostsFromFilesystem(): Promise<BlogPost[]> {
	const blogDir = path.join(process.cwd(), "pages", "blog");
	const mdxFiles = await collectMdxFiles(blogDir);

	const posts = await Promise.all(
		mdxFiles.map(async (filePath) => {
			const source = await fs.readFile(filePath, "utf8");
			const frontMatter = parseFrontMatter(source);
			const route = `/blog/${path
				.relative(blogDir, filePath)
				.replace(/\\/g, "/")
				.replace(/\.mdx$/, "")}`;

			return {
				route,
				frontMatter: {
					title: frontMatter.title || route,
					date: frontMatter.date,
					author: frontMatter.author,
					description: frontMatter.description,
				},
			} satisfies BlogPost;
		}),
	);

	return posts.sort((a, b) => {
		const dateA = a.frontMatter.date ? new Date(a.frontMatter.date).getTime() : 0;
		const dateB = b.frontMatter.date ? new Date(b.frontMatter.date).getTime() : 0;
		return dateB - dateA;
	});
}

export const getStaticProps: GetStaticProps<{ posts: BlogPost[] }> = async () => {
	const posts = await getBlogPostsFromFilesystem();

	return {
		props: {
			posts,
		},
	};
};

export default function Home({ posts }: InferGetStaticPropsType<typeof getStaticProps>) {
	return (
		<>
			<Head>
				<title>Samuel Scheit</title>
				<meta name="description" content="Samuel Scheit - Developer, Student, Founder" />
				<meta name="og:description" content="Samuel Scheit - Developer, Student, Founder" />
				<link rel="preload" crossOrigin="anonymous" type="font/woff2" as="font" href="/fonts/inter-v12-latin-900.woff2" />
				<link rel="preload" crossOrigin="anonymous" type="font/woff2" as="font" href="/fonts/inter-v12-latin-600.woff2" />
				<link rel="preload" crossOrigin="anonymous" type="font/woff2" as="font" href="/fonts/inter-v12-latin-regular.woff2" />
			</Head>
			<div className="main">
				<div className="links-wrapper">
					<Links />
				</div>
				<div className="content">
					<Hero />
					<BlogPosts posts={posts} />
					<Projects />
					<About />
					<Contact />
				</div>
				<div className="links-wrapper" style={{ width: "100px", zIndex: -1 }}></div>
				<div className="honeypot" style={{ display: "none" }}>
					<a href="mailto:bluestacksplayer380@icloud.com">bluestacksplayer380@icloud.com</a>
					<a href="mailto:bluestacksplayer380@gmail.com">bluestacksplayer380@gmail.com</a>
				</div>
			</div>
		</>
	);
}
