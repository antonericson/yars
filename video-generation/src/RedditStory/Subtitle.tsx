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
    numberOfFrames: number;
}> = ({ titleText, audioFile, numberOfFrames }) => {
    const videoConfig = useVideoConfig();
    const frame = useCurrentFrame();
    const text = titleText.split(' ').map((t) => ` ${t} `);
    const nWords = text.length;
    let usedFrames = 0;
    let nFramesToUse = 0;
    return (
        <>
            <Audio src={staticFile(audioFile)} />
            <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,600,300" rel="stylesheet" type="text/css" />
            <div style={{
                height: '100%',
                width: '100%',
                marginTop: '60%',
                alignContent: 'center',
            }}>
                <div style={{
                    margin: '0 1em 0 1em',
                    paddingBottom: '1em',
                    paddingTop: '.5em',
                    background: 'rgba(0, 0, 0, 0.3)',
                    borderRadius: '1em'
                }}>
                    <h1
                        style={{
                            textAlign: 'center',
                            fontFamily: 'Open Sans',
                            fontStyle: 'bold',
                            fontWeight: 600,
                            fontSize: '5.3em',
                            lineHeight: '98px',
                            color: '#FFFFFF',
                            WebkitTextStroke: '4px #000000'
                        }}
                    >

                        {text.map((t, i) => {

                            if (i === 0) {
                                usedFrames = 0
                            } else {
                                nFramesToUse = Math.round((numberOfFrames * 0.80 - usedFrames) / (nWords - i + 1))
                                usedFrames = usedFrames + nFramesToUse
                            }

                            return (
                                <span
                                    key={t + '-' + i}
                                    style={{
                                        color: 'white',
                                        marginLeft: 20,
                                        marginRight: 20,
                                        transform: `scale(${spring({
                                            fps: videoConfig.fps,
                                            frame: frame - usedFrames,
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
                </div>
            </div>
        </>
    );
};
