import Link from "next/link";

export type BlogPost = {
	route: string;
	frontMatter: {
		title: string;
		date?: string;
		author?: string;
		description?: string;
	};
};

export function BlogPosts({ posts }: { posts: BlogPost[] }) {
	if (posts.length === 0) return null;

	return (
		<section className="blogposts" id="blog">
			<h2>Blog</h2>

			<div className="posts">
				{posts.map(({ frontMatter, route }) => (
					<Link prefetch={false} href={route} key={route} className="post">
						<h3 className="title">{frontMatter.title}</h3>
						{frontMatter.description && (
							<p className="description">
								{frontMatter.description}
								{frontMatter.date && (
									<span className="date">
										{new Date(frontMatter.date).toLocaleDateString("en-US", {
											dateStyle: "medium",
										})}
									</span>
								)}
							</p>
						)}
					</Link>
				))}
			</div>
		</section>
	);
}
