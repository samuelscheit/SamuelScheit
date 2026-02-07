import nextra from "nextra";

const withNextra = nextra({});

/** @type {import('next').NextConfig} */
const nextConfig = {
	reactStrictMode: true,
	images: {
		unoptimized: true,
	},
	experimental: {
		scrollRestoration: true,
	},
	webpack: (config, { buildId, dev, isServer, defaultLoaders, nextRuntime, webpack }) => {
		config.module.rules.push({
			test: /\.svg$/i,
			use: ["@svgr/webpack"],
		});

		const nextExportImageLoader = config.module.rules.find(
			({ use }) => use && use.length > 0 && use[0]?.loader === "next-export-optimize-images-loader",
		);
		if (nextExportImageLoader) {
			nextExportImageLoader.test = /\.(png|jpg|jpeg|gif|webp|avif|ico|bmp)$/i; // Removed only svg
		}

		return config;
	},
	output: "export",
};

export default withNextra(nextConfig);
