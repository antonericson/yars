import { interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig, OffthreadVideo } from 'remotion';
import { Subtitle } from './RedditStory/Subtitle';
import { Attribution } from './RedditStory/Attribution';

export const RedditStory: React.FC<{
	sentences: Array<string>,
	videoLengths: Array<number>,
	author: string,
	subreddit: string
}> = ({ sentences, videoLengths, author, subreddit }) => {
	const frame = useCurrentFrame();
	const videoConfig = useVideoConfig();

	const opacity = interpolate(
		frame,
		[videoConfig.durationInFrames - 25, videoConfig.durationInFrames - 15],
		[1, 0],
		{
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
		}
	);
	const transitionStart = 25;

	const sequences = () => {
		let result: JSX.Element[] = []
		let seq = undefined
		let from = transitionStart
		let numberOfFrames = undefined
		sentences.forEach((sentence, index) => {
			 numberOfFrames = videoLengths[index] * 30
			if (index < sentences.length - 1) {
				seq = <Sequence from={from} key={index} durationInFrames={numberOfFrames}>
					<Subtitle
						titleText={sentence}
						audioFile={`audio/${index}.wav`}
						numberOfFrames={numberOfFrames} />
				</Sequence>
			} else {
				seq = <Sequence from={from} key={index}>
					<Subtitle
						titleText={sentence}
						audioFile={`audio/${index}.wav`}
						numberOfFrames={numberOfFrames} />
				</Sequence>
			}
			from = from + Math.round((30 * videoLengths[index])) + 5
			result.push(seq)
		})
		return result
	}
	return (
		<div style={{flex: 1}}>
			<OffthreadVideo
				muted
				startFrom={60}
				src={staticFile(`video/backgroundVideo.mp4`)}
				style={{
					objectFit: 'cover',
					width: '100%',
					height: '100%'
				}} />
				<div style={{ opacity }}>
					{sequences()}
				</div>
			<Attribution author={author} subreddit={subreddit}/>
		</div>
	);
};
