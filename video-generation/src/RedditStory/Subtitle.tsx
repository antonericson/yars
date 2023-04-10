import {
	Audio,
	spring,
	useCurrentFrame,
	useVideoConfig,
	staticFile
} from 'remotion';

export const Subtitle: React.FC<{
	titleText: string;
	audioFile: string;
}> = ({titleText, audioFile}) => {
	const videoConfig = useVideoConfig();
	const frame = useCurrentFrame();
	const text = titleText.split(' ').map((t) => ` ${t} `);

	return (
		<>
			<Audio src={staticFile(audioFile)} />
			<h1
				style={{
					fontFamily: 'SF Pro Text, Helvetica, Arial',
					fontWeight: 'bold',
					fontSize: 70,
					textAlign: 'center',
					position: 'absolute',
					bottom: '50%',
					width: '100%',
					zIndex: 99,
					WebkitTextStroke: '2px black'
				}}
			>
				{text.map((t, i) => {
					return (
						<span
							key={t+'-'+i}
							style={{
								color: 'white',
								marginLeft: 20,
								marginRight: 20,
								transform: `scale(${spring({
									fps: videoConfig.fps,
									frame: frame - i * 5,
									config: {
										damping: 100,
										stiffness: 200,
										mass: 0.5,
									},
								})})`,
								display: 'inline-block',
							}}
						>
							{t}
						</span>
					);
				})}
			</h1>
		</>
	);
};
