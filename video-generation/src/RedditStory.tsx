import { interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig, OffthreadVideo } from 'remotion';
import { Subtitle } from './RedditStory/Subtitle';
import { Attribution } from './RedditStory/Attribution';

export const RedditStory: React.FC<{
	backgroundVideoName: string,
	sentences: Array<string>,
	videoLengths: Array<number>,
	author: string,
	subreddit: string
}> = ({ backgroundVideoName, sentences, videoLengths, author, subreddit }) => {
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
		sentences.forEach((sentence, index) => {
			if (index < sentences.length - 1) {
				seq = <Sequence from={from} durationInFrames={videoLengths[index] * 30 + 5}>
					<Subtitle
						titleText={sentence}
						audioFile={`audio/${index}.wav`}
						titleColor={"black"} />
				</Sequence>
			} else {
				seq = <Sequence from={from}>
					<Subtitle
						titleText={sentence}
						audioFile={`audio/${index}.wav`}
						titleColor={"black"} />
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
				src={staticFile(`video/${backgroundVideoName}`)}
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
