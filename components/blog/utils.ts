import { useRouter } from "next/router";
import type { Folder, MdxFile, PageMapItem } from "nextra";

export default function traverse(pageMap: PageMapItem[], matcher: (page: PageMapItem) => boolean | void): PageMapItem | null {
	for (const pageMapItem of pageMap) {
		if (matcher(pageMapItem)) {
			return pageMapItem;
		}
	}

	for (const item of pageMap) {
		if ("children" in item) {
			const matched = traverse(item.children, matcher);
			if (matched) {
				return matched;
			}
		}
	}
	return null;
}

type LayoutLikeProps = {
	opts: {
		pageMap: PageMapItem[];
	};
};

export function getParent({ opts }: LayoutLikeProps) {
	let back: string | null = null;
	const parentPages: (MdxFile | Folder)[] = [];
	// eslint-disable-next-line react-hooks/rules-of-hooks
	const { route } = useRouter();

	traverse(opts.pageMap, (page) => {
		if ("route" in page && route !== page.route && (route + "/").startsWith(page.route === "/" ? "/" : page.route + "/")) {
			parentPages.push(page);
		}
	});

	const parentPage = parentPages.reverse().find((page) => "frontMatter" in page && page.frontMatter && page.frontMatter.type === "posts");

	if (parentPage) {
		back = parentPage.route;
	}

	return { parentPage, back };
}
