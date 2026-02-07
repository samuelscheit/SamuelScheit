import { useMDXComponents as getNextraMDXComponents } from "nextra/mdx-components";
import type { MDXComponents } from "nextra/mdx-components";
import { BlogWrapper, blogMdxComponents } from "./components/blog/theme";

const defaultComponents = getNextraMDXComponents({
	...blogMdxComponents,
	wrapper: BlogWrapper,
});

export function useMDXComponents(components: MDXComponents = {}) {
	return {
		...defaultComponents,
		...components,
	};
}
