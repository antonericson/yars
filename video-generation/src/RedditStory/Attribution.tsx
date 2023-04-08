
export const Attribution: React.FC<{
    author: string,
    subreddit: string
}> = ({ author, subreddit }) => {

    return (
        <>
            <div
                style={{
                    fontFamily: 'SF Pro Text, Helvetica, Arial',
					fontSize: 40,
					textAlign: 'left',
					position: 'absolute',
					bottom: '5%',
                    paddingLeft: '30px',
					width: '50%',
					zIndex: 99,
					WebkitTextStroke: '1px white'
                }}
            >
            <p>Author: {author}<br/>r/{subreddit}</p>
            </div>
        </>
    )
}