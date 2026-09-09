import React, { useRef, useEffect } from "react";

export function Timeline(props: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>) {
	const sectionRef = useRef<HTMLDivElement>(null);
	const trackRef = useRef<HTMLDivElement>(null);
	const shadowTopRef = useRef<HTMLDivElement>(null);
	const shadowBottomRef = useRef<HTMLDivElement>(null);
	const { children, className, style, ...sectionProps } = props;

	useEffect(() => {
		const section = sectionRef.current;
		if (!section) return;

		function handleScroll() {
			if (!section) return;
			if (!trackRef.current) return;

			const rect = section.getBoundingClientRect();
			const middle = window.innerHeight / 2;
			// Calculate offset: 0 until timeline reaches middle, then increase
			const offset = rect.top * -1;
			trackRef.current!.style.top = `${offset}px`;

			// Show/hide shadows based on scroll position
			const sectionTop = rect.top;
			const sectionBottom = rect.bottom;
			const windowHeight = window.innerHeight;

			// Show top shadow when we can scroll up (section is below top of viewport)
			if (shadowTopRef.current) {
				shadowTopRef.current.style.opacity = sectionTop < 0 ? "1" : "0";
			}

			// Show bottom shadow when we can scroll down (section extends below viewport)
			if (shadowBottomRef.current) {
				shadowBottomRef.current.style.opacity = sectionBottom > windowHeight ? "1" : "0";
			}
		}

		window.addEventListener("scroll", handleScroll, { passive: true });
		handleScroll();
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	return (
		<section
			ref={sectionRef}
			{...sectionProps}
			style={{ zIndex: 0, ...style }}
			className={["timeline", className].filter(Boolean).join(" ")}
		>
			<div className="bar">
				<div className="overlay-fade-top" />
				<div ref={trackRef} className="track"></div>
				<div className="overlay-fade-bottom" />
			</div>
			<div ref={shadowTopRef} className="shadow-top" />
			{children}
			<div ref={shadowBottomRef} className="shadow-bottom" />
		</section>
	);
}

export function TimelineItem(
	props: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement> & {
		date?: string | Date;
		title?: string;
		text?: string;
		titleStyle?: React.CSSProperties;
	}
) {
	return (
		<div style={props.style} className="item">
			<div className="date">{props.date instanceof Date ? props.date.toDateString() : props.date}</div>
			<div className="dot" />
			<div className="content">
				{props.title && <h2 style={props.titleStyle}>{props.title}</h2>}
				{props.text?.split("\n").map((x) => (
					<p key={x}>
						{x}
						<br />
					</p>
				)) || props.children}
			</div>
		</div>
	);
}
