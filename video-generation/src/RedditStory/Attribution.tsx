
export const Attribution: React.FC<{
    author: string,
    subreddit: string
}> = ({ author, subreddit }) => {

    return (
        <>
            <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,600,300" rel="stylesheet" type="text/css" />
            <div
                style={{
                    fontFamily: 'Open Sans',
                    fontStyle: 'bold',
                    fontWeight: 600,
                    fontSize: '3em',
                    color: 'white',
                    textAlign: 'left',
                    position: 'absolute',
                    bottom: '5%',
                    paddingLeft: '30px',
                    width: '50%',
                    zIndex: 99,
                    WebkitTextStroke: '1px black'
                }}
            >
                <p>Author: {author}<br/>r/{subreddit}</p>
            </div>
        </>
    )
}