import Link from "next/link";
import { Code, Pre, Table } from "nextra/components";
import type { MDXComponents } from "nextra/mdx-components";
import type { $NextraMetadata, MDXWrapper } from "nextra";
import { ComponentProps, ReactElement, ReactNode } from "react";
import type { UrlObject } from "url";
import { Links } from "../Links";
import { Link as ExternalLink } from "../Link";
import Head from "next/head";

type BlogMetadata = $NextraMetadata & {
	date?: string;
	description?: string;
	tags?: string;
	language?: string;
};

const H1 = () => null;
type LinkHref = string | UrlObject;
type AnchorProps = Omit<ComponentProps<"a">, "href"> & { href?: LinkHref };

function HeadingLink({
	tag: Tag,
	children,
	id,
	className,
	...props
}: ComponentProps<"h2"> & { tag: `h${2 | 3 | 4 | 5 | 6}` }): ReactElement {
	return (
		<Tag
			id={id}
			className={
				// can be added by footnotes
				className === "sr-only" ? "sr-only" : `subheading-${Tag}`
			}
			{...props}
		>
			{children}
			{id && <a href={`#${id}`} className="not-prose subheading-anchor" aria-label="Permalink for this section" />}
		</Tag>
	);
}

function toHrefString(href?: LinkHref): string {
	if (typeof href === "string") return href;
	if (!href) return "";
	if (typeof href.pathname === "string") return href.pathname;
	return "";
}

const A = ({ children, href, ...props }: AnchorProps): ReactElement => {
	const hrefString = toHrefString(href);
	if (hrefString.startsWith("#")) {
		return (
			<a href={hrefString} {...props}>
				{children}
			</a>
		);
	}

	return (
		<ExternalLink href={hrefString} {...props}>
			{children as ReactNode}
		</ExternalLink>
	);
};

export const blogMdxComponents: MDXComponents = {
	h1: H1,
	h2: (props) => <HeadingLink tag="h2" {...props} />,
	h3: (props) => <HeadingLink tag="h3" {...props} />,
	h4: (props) => <HeadingLink tag="h4" {...props} />,
	h5: (props) => <HeadingLink tag="h5" {...props} />,
	h6: (props) => <HeadingLink tag="h6" {...props} />,
	a: A,
	pre: ({ children, ...props }) => (
		<Pre className="not-prose" {...props}>
			{children}
		</Pre>
	),
	tr: Table.Tr,
	th: Table.Th,
	td: Table.Td,
	table: (props) => <Table className="not-prose" {...props} />,
	code: Code,
};

function parseDate(date?: string): Date | null {
	if (!date) return null;
	const parsed = new Date(date);
	return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function parseTags(tags?: string): string[] {
	if (!tags) return [];
	return tags
		.split(",")
		.map((tag) => tag.trim())
		.filter(Boolean);
}

export const BlogWrapper: MDXWrapper = ({ children, metadata }) => {
	const blogMetadata = metadata as BlogMetadata;
	const title = blogMetadata.title;
	const date = parseDate(blogMetadata.date);
	const tags = parseTags(blogMetadata.tags);
	const { language } = blogMetadata;
	const isEn = language !== "de";
	const description = blogMetadata.description;

	return (
		<>
			<div className="main blog">
				<Head>
					<title>{title}</title>
					{description ? <meta name="og:description" content={description} /> : null}
				</Head>
				<div className="links-wrapper">
					<Links>
						<Link href="/" title="Back" className="x:absolute x:max-md:hidden" style={{ left: "30px", top: "40px" }}>
							<svg xmlns="http://www.w3.org/2000/svg" width="2.3rem" height="2.3rem" viewBox="0 0 24 24">
								<path fill="currentColor" d="m15.914 17.5l-5.5-5.5l5.5-5.5L14.5 5.086L7.586 12l6.914 6.914z"></path>
							</svg>
						</Link>
					</Links>
				</div>
				<article
					className="x:container x:prose x:max-md:prose-sm x:!pt-6 x:dark:prose-invert x:relative"
					dir="ltr"
					style={{ fontSize: "18px" }}
				>
					<div className="x:flex x:justify-center x:z-10 x:pb-10">
						<Link
							href={"/"}
							className="x:text-center x:p-4 x:text-4xl x:font-bold x:bg-clip-text x:!text-transparent"
							style={{
								backgroundImage: "linear-gradient(90deg, rgba(0,124,240,1) 23%, rgba(0,223,216,1) 71%)",
								textDecoration: "none",
							}}
						>
							Samuel Scheit
						</Link>
					</div>

					<h1 style={{ textAlign: "center" }}>{title}</h1>

					<div className="x:flex x:flex-row x:w-full x:text-xs x:text-center x:gap-6 x:items-center">
						{date ? (
							<time className=" x:font-mono " dateTime={date.toISOString()}>
								{date.toLocaleDateString("en-US", {
									dateStyle: "long",
								})}
							</time>
						) : null}
						{tags.length > 0 ? (
							<div className="x:flex x:justify-center x:gap-2 x:items-center">
								{tags.map((tag) => (
									<div key={tag} className="x:text-sm x:bg-gray-50 x:dark:bg-gray-900 x:p-2 x:rounded-md">
										{tag}
									</div>
								))}
							</div>
						) : null}
					</div>

					{children}

					<footer className="x:mt-20 x:mb-40 x:text-center x:flex x:flex-col x:gap-2">
						<div className="x:text-2xl x:font-semibold x:mb-4">{isEn ? `Thank you for reading!` : `Danke fürs lesen!`}</div>
						<div>
							{isEn
								? "If you want to support me you can sponsor me on "
								: "Wenn du mich unterstützen möchtest kannst du mir spenden auf "}
							<ExternalLink
								style={{ textDecoration: "none", fontWeight: 600 }}
								href="https://github.com/sponsors/SamuelScheit"
							>
								GitHub
							</ExternalLink>{" "}
							🫶
						</div>
						<div>
							{isEn
								? `If you have any questions or feedback, feel free to contact me. 👨‍💻`
								: `Wenn du Fragen oder Feedback hast, kannst du mir gerne schreiben. 👨‍💻`}
						</div>
						<div className="contact-links links-wrapper x:mt-20">
							<Links />
						</div>
					</footer>
				</article>
				<div className="links-wrapper" style={{ width: "100px" }}></div>
			</div>
		</>
	);
};
