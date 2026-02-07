import Image from "next-image-export-optimizer";
import { Timeline, TimelineItem } from "./timeline";
import { Link } from "./Link";

export function About() {
	return (
		<div id="about">
			<h2
				style={{
					background: "var(--background)",
					flex: 1,
					zIndex: 1,
					position: "relative",
					textAlign: "center",
					paddingBottom: "3rem",
					paddingTop: "10rem",
					fontSize: "4rem",
					fontWeight: 700,
				}}
			>
				About
			</h2>
			<Timeline>
				<TimelineItem style={{ paddingTop: "2rem" }} date="November 2003" title="">
					<div>
						I was born in November 2003 in Munich, Germany. <br /> <br /> My father grew up in Konstanz, Germany, and studied
						technical computer science, while my grandfather studied electrical engineering. <br /> <br />
						Since both my father and grandfather worked in computer engineering, they both had an interest in introducing me to
						technology at an early age.
					</div>
				</TimelineItem>
				<TimelineItem date="August 2014" title="Learning programming">
					<div>
						I enjoyed playing video games, like many children my age. However, I had to share the family computer with my{" "}
						<Link href="https://linktr.ee/GxdAim">brother</Link> and parents. <br /> <br /> As a result, I asked my
						(grand)parents for my own computer, and after negotiating they agreed to purchase one for me if I learned
						programming first. <br /> <br /> I learned the <Link href="https://www.c-howto.de/">C</Link> programming language
						because it was the only one they could help me with. I used it to program a Sudoku solver and helped my grandfather
						solve sudokus with it.
					</div>
				</TimelineItem>
				<TimelineItem date="November 2015" title="A personal computer">
					<div>
						As promised, I received my first personal computer, which I of course used for <del>programming</del> playing
						Minecraft. <br /> <br /> Within the game, I liked using &quot;command blocks and redstone&quot;, which are similar
						to logic gates and simple programming constructs.
						<br /> <br /> However, playing alone was not as enjoyable as playing with friends, so I learned how to host servers
						for them.
					</div>
				</TimelineItem>
				<TimelineItem date="June 2016" title="Linux">
					<div>
						I wanted to host multiple Minecraft servers and needed to find a way to keep them running without constantly relying
						on my personal computer. <br /> <br /> I used an old laptop from my parents&apos; work and installed Linux, as it
						was much more efficient and able to host multiple servers at the same time. <br /> Through this process, I learned a
						lot about operating systems and hosting servers. <br /> <br /> However, I encountered a problem with managing
						multiple servers, as I did not have an overview of them.
					</div>
				</TimelineItem>
				<TimelineItem date="February 2017" title="Web development">
					<div>
						I wanted to create a website that provided an overview of my Minecraft servers, so I had to learn HTML and CSS.
						<br /> <br /> However, a static website just for viewing was not enough, I also wanted to manage those servers.
						<br /> For this, I learned PHP and SQL to make the site interactive and store the servers in a database.
						<br /> <br /> This project marked the beginning of my journey as a developer and the start of many{" "}
						<a className="hover-animation" href="#projects">
							subsequent projects
						</a>
						.
					</div>
				</TimelineItem>
				<TimelineItem date="September 2018" title="School">
					<div>
						Because I was part of a tablet class, my classmates and I wanted to exchange ideas and collaborate on our tablets.
						<br /> <br /> However, since there was no existing{" "}
						<Link href={"https://github.com/SamuelScheit/Tabletklasse"}>communication platform</Link> provided by the school, I
						developed one myself for my classmates to communicate and work together on projects. <br /> <br /> As I continued, I
						pivoted my project to a{" "}
						<Link href="https://apps.apple.com/de/app/gyki/id1449048723?platform=iphone">mobile app</Link> for my school, which
						allowed students to view the substitution plan, timetable, and appointments in one easy-to-use interface.
					</div>
				</TimelineItem>
				<TimelineItem date="March 2019" title="Discord">
					<div>
						Alongside my school platform, I used Discord for private communication and wanted to extend the platform. <br />
						<br /> I started programming various <Link href="https://github.com/SamuelScheit/discord-bots">
							Discord bots
						</Link>{" "}
						and gained experience doing commissioned work. <br /> <br /> To make it easier to oversee my bots, I needed a
						user-friendly interface and I developed a tool called{" "}
						<Link href="https://github.com/SamuelScheit/discord-bot-client">Discord Bot Client</Link>. <br /> <br /> But as it
						made use of Discord&apos;s official client, Discord shut it down alongside my account and all of my bots.
					</div>
				</TimelineItem>
				<TimelineItem date="January 2021" title="Fosscord">
					<div>
						I wanted to create an alternative platform to Discord that is free, open-source, and can be self-hosted. <br />
						<br /> However, I still wanted to be able to communicate with my friends and use the bots I had made prior. <br />
						<br /> That is why I founded <Link href="https://spacebar.chat/">Fosscord</Link> (now Spacebar Chat), a platform
						that is backwards compatible with Discord and that enables users to have control over their conversations while
						still being able to use Discord clients, bots, and libraries.
					</div>
				</TimelineItem>
				<TimelineItem date="January 2022" title="Respond">
					<div>
						For Fosscord, I wanted to create an independent client that could be used to connect to both Discord and Fosscord.
						<br /> <br /> However, I realized that I could further extend the project and create a client that is not only
						limited to Discord/Fosscord. <br /> <br /> That is why I founded <Link href="https://respond.chat/">Respond</Link>,
						a messenger that allows users to reach their friends no matter what platform they use e.g. WhatsApp, Telegram,
						Discord/Fosscord.
					</div>
				</TimelineItem>
			</Timeline>
		</div>
	);
}
