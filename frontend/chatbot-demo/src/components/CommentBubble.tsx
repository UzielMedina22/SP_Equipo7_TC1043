type CommentBubble = {
    name: string,
    date: string,
    message: string
}

export default function CommentBubble({name, date, message}: CommentBubble) {
    let bubbleClass = ""
    let nameClass = "";
    
    bubbleClass = name == "IKEA-Bot" ? "comment-bot" : "comment-user"
    nameClass = name == "IKEA-Bot" ? "comment-bot-name" : "comment-user-name"

    return (
        <div className={`w-3/4 p-2 ${bubbleClass} shadow-2xl`}>
            <div className="inline-flex pb-2">
                <p className={`${nameClass}`}>{name}</p>
                <p>&nbsp;&nbsp;{`${date}`}</p>
            </div>
            <p>{message}</p>
        </div>
    )
}