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

		return config;
	},
	turbopack: {
		rules: {
			"*.svg": {
				loaders: ["@svgr/webpack"],
				as: "*.js",
			},
		},
	},
	output: "export",
	images: {
		loader: "custom",
		imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
		deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
	},
	transpilePackages: ["next-image-export-optimizer"],
	env: {
		nextImageExportOptimizer_imageFolderPath: "public/images",
		nextImageExportOptimizer_exportFolderPath: "out",
		nextImageExportOptimizer_quality: "75",
		nextImageExportOptimizer_storePicturesInWEBP: "true",
		nextImageExportOptimizer_exportFolderName: "img",
		nextImageExportOptimizer_generateAndUseBlurImages: "true",
		nextImageExportOptimizer_remoteImageCacheTTL: "31536000",
	},
};

export default withNextra(nextConfig);
