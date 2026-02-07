import Avatar from "../public/avatar.png";
import Image from "next-image-export-optimizer";

function RepeatFirstElement(
	props: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement> & {
		children: React.ReactNode[];
	},
) {
	return (
		<div {...props}>
			{props.children}
			{props.children[0]}
		</div>
	);
}

export function Hero(props: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>) {
	return (
		<section {...props} className="hero">
			<div className="navigation">
				<a className="hover-animation" href="#projects">
					Projects
				</a>
				<a className="hover-animation" href="#about">
					About
				</a>
				<a className="hover-animation" href="#contact">
					Contact
				</a>
			</div>
			<div className="grid">
				<div className="title">
					<h1>Samuel Scheit</h1>
					<div className="subtitle">
						<RepeatFirstElement className="wrapper">
							<h2
								style={{
									backgroundImage: "linear-gradient(90deg, #007CF0, #00DFD8)",
								}}
							>
								Developer
							</h2>
							<h2
								style={{
									backgroundImage: "linear-gradient(90deg, #7928CA, #FF0080)",
								}}
							>
								Freelancer
							</h2>
							<h2
								style={{
									backgroundImage: "linear-gradient(90deg, #FF4D4D, #F9CB28)",
								}}
							>
								Founder
							</h2>
						</RepeatFirstElement>
					</div>
				</div>
				<div className="avatar">
					<Image priority width={250} src={Avatar} alt="Samuel Scheit" />
				</div>
			</div>
			<div></div>
		</section>
	);
}
