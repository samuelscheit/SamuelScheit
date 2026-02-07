import { ReactNode, useEffect } from "react";
import Image from "next/image";
import Spacebar from "../public/projects/spacebar.png";
import DiscordBotClient from "../public/projects/discord_bot_client.png";
import CarcassonneAI from "../public/projects/carcassonne_ai.png";
import Fingerprinting from "../public/projects/fingerprinting.png";
import PuppeteerStream from "../public/projects/puppeteer_stream.png";
import Link from "next/link";

export function Card(props: { href?: string; children: ReactNode }) {
	return (
		<a rel="noreferrer" target="_blank" href={props.href} className="card">
			<div className="glow" />
			{props.children}
		</a>
	);
}

export function Projects() {
	useEffect(() => {
		const cards = document.querySelectorAll(".projects .card") as any;

		function rotateToMouse(this: any, e: any) {
			const mouseX = e.clientX;
			const mouseY = e.clientY;

			this.bounds = this.getBoundingClientRect();

			const leftX = mouseX - this.bounds.x;
			const topY = mouseY - this.bounds.y;

			this.querySelector(".glow").style.setProperty("--x", `${leftX}px`);
			this.querySelector(".glow").style.setProperty("--y", `${topY}px`);
		}

		const listeners = [] as any[];

		for (const $card of cards) {
			const rotate = rotateToMouse.bind($card);
			listeners.push(rotate);

			document.addEventListener("mousemove", rotate);
		}

		return () => {
			for (const listener of listeners) {
				document.removeEventListener("mousemove", listener);
			}
		};
	}, []);

	return (
		<section className="projects" id="projects">
			<h2
				style={{
					fontSize: "4rem",
					textAlign: "center",
					marginTop: "4rem",
					marginBottom: "4rem",
				}}
			>
				Projects
			</h2>
			<div className="projects-container">
				<div className="list">
					<Card href="https://spacebar.chat">
						<Image style={{ aspectRatio: "2 / 1" }} src={Spacebar} alt="Spacebar" />
					</Card>
					<Card href="https://github.com/SamuelScheit/discord-bot-client">
						<Image style={{ aspectRatio: "2 / 1" }} src={DiscordBotClient} alt="Discord Bot Client" />
					</Card>
					<Card href="https://github.com/SamuelScheit/puppeteer-stream">
						<Image style={{ aspectRatio: "2 / 1" }} src={PuppeteerStream} alt="Puppeteer stream" />
					</Card>
					<Card href="https://github.com/SamuelScheit/fingerprinting">
						<Image style={{ aspectRatio: "2 / 1" }} src={Fingerprinting} alt="Browser Fingerprinting" />
					</Card>
				</div>

				<div className="more-button-container">
					<Link href="/github" className="more-button">
						More
					</Link>
				</div>
			</div>
		</section>
	);
}
