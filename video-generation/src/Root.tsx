import {Composition, getInputProps} from 'remotion';
import { RedditStory } from './RedditStory';

export const RemotionRoot: React.FC = () => {
    const props = getInputProps()

    return (
        <>
            <Composition
                id="RedditStory"
                component={RedditStory}
                durationInFrames={Math.round(30 * props.totalLength) + 60}
                fps={30}
                width={1080}
                height={1920}
                defaultProps={{
                    sentences: props.sentences,
                    videoLengths: props.videoLengths,
                    author: props.author,
                    subreddit: props.subreddit
                }}
            />
        </>
    );
};
