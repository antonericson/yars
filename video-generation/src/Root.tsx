import {Composition, getInputProps} from 'remotion';
import { RedditStory } from './RedditStory';

export const RemotionRoot: React.FC = () => {
	let props = getInputProps()
	const totalVideoFrames = Math.round(30 * props.totalLength) + 60
	console.log(props)
	const getRandomIntInclusive = (min: number, max: number) => {
		min = Math.ceil(min);
		max = Math.floor(max);
		return Math.floor(Math.random() * (max - min + 1) + min);
	}

	const getStartTime = () => {
		return getRandomIntInclusive(0, props.backgroundVideoFrameCount - totalVideoFrames - 60)
	}

	const startFrame = getStartTime()
	return (
		<>
			<Composition
				id="RedditStory"
				component={RedditStory}
				durationInFrames={totalVideoFrames}
				fps={30}
				width={1080}
				height={1920}
				defaultProps={{
					backgroundVideoName: props.backgroundVideoName,
					startFrame: startFrame,
					sentences: props.sentences,
					videoLengths: props.videoLengths,
					author: props.author,
					subreddit: props.subreddit
				}}
			/>
		</>
	);
};
