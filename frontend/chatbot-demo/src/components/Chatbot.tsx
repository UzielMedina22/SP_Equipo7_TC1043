import { useEffect, useState } from "react";
import { talkWithLLM } from "../api/chatbot";
import CommentBubble from "./CommentBubble";

// Formatear la fecha del usuario.
function formatUserDate(date: string) {
  const day = date.substring(8, 10)
  const month = date.substring(4, 7)
  let monthNumber = ""
  const year = date.substring(11, 15)
  const hour = date.substring(16, 21)

  switch (month) {
    case "Jan":
      monthNumber = "01";
      break;
    case "Feb":
      monthNumber = "02";
      break;
    case "Mar":
      monthNumber = "03";
      break;
    case "Apr":
      monthNumber = "04";
      break;
    case "May":
      monthNumber = "05";
      break;
    case "Jun":
      monthNumber = "06";
      break;
    case "Jul":
      monthNumber = "07";
      break;
    case "Aug":
      monthNumber = "08";
      break;
    case "Sep":
      monthNumber = "09";
      break;
    case "Oct":
      monthNumber = "10";
      break;
    case "Nov":
      monthNumber = "11";
      break;
    case "Dec":
      monthNumber = "12";
      break;
    default:
      monthNumber = "00";
      break; 
  }

  return `${day}/${monthNumber}/${year}  ·  ${hour}`
}

// Formatear la fecha del chatbot.
function formatBotDate(date: string) {
  const day = date.substring(8, 10)
  const month = date.substring(5, 7)
  const year = date.substring(0, 4)
  const hour = date.substring(11, 16)

  return `${day}/${month}/${year}  ·  ${hour}`
}

export default function Chatbot({ className = "" }) {
  const [currentPrompt, setCurrentPrompt] = useState("")
  const [chatHistory, setChatHistory] = useState([])
  const [loadingAnswer, setLoadingAnswer] = useState(false)
  let isFirstPrompt = true

  const handlePrompt = (prompt: string) => {
    talkWithLLM(prompt)
    .then((res) => {
      setLoadingAnswer(false);
      setChatHistory((prevChat) => [...prevChat, { name: "IKEA-Bot", date: formatBotDate(res.date), message: res.chatbot_response }])
    })
    .catch(() => setLoadingAnswer(false))
  }

  useEffect(() => {
    if (isFirstPrompt) {
      setLoadingAnswer(true)
      handlePrompt("Hola.")
      isFirstPrompt = false
    }
  }, [])

  return (
    <div className={`${className} mx-auto bg-white shadow-lg`} style={{borderRadius: 12}}>
      <div className="w-full chat-panel-header px-4 flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-white">IKEA-Bot</h2>
      </div>
      <div className="px-4 h-100 overflow-scroll">
        {
          chatHistory.map((comment, idx) => (
            <div className={`w-full ${idx > 0 ? "mt-4" : ""} ${comment.name == "IKEA-Bot"? "" : "justify-items-end"}`}>
              <CommentBubble name={comment.name} date={comment.date} message={comment.message} />
            </div>
          ))
        }
      </div>
      <div className="inline-flex gap-4 items-center chat-panel-footer w-full px-4 py-2" style={ { backgroundColor: "#0058A3" } }>
        <input 
          className="shadow-lg chat-panel-input w-full px-4 h-20" 
          type="text"
          disabled={loadingAnswer}
          placeholder={loadingAnswer? "Esperando a IKEA-Bot..." : "Ingresa un mensaje para interactuar."}
          value={ currentPrompt }
          onChange={(e) => { if (currentPrompt !== null) { setCurrentPrompt(e.target.value) }}}
          onKeyDown={(e) => { 
            if (e.key === "Enter" && currentPrompt !== null && currentPrompt.trim() != "") { 
              setLoadingAnswer(true)
              const userPromptDate = formatUserDate(Date())
              const processedPrompt = e.target.value.trim()
              setChatHistory([...chatHistory, { name: "Tú", date: userPromptDate, message: processedPrompt }])
              setCurrentPrompt("")
              handlePrompt(processedPrompt)
            }}}
          />

        <button className={`${loadingAnswer ? "" : "chat-panel-send-button"} p-2`} disabled={loadingAnswer} 
          onClick={()=>{}}>
          <svg className={`${loadingAnswer ? "text-gray-300" : "text-white"}`} width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.4995 13.5001L20.9995 3.00005M10.6271 13.8281L13.2552 20.5861C13.4867 21.1815 13.6025 21.4791 13.7693 21.566C13.9139 21.6414 14.0862 21.6415 14.2308 21.5663C14.3977 21.4796 14.5139 21.1821 14.7461 20.587L21.3364 3.69925C21.5461 3.16207 21.6509 2.89348 21.5935 2.72185C21.5437 2.5728 21.4268 2.45583 21.2777 2.40604C21.1061 2.34871 20.8375 2.45352 20.3003 2.66315L3.41258 9.25349C2.8175 9.48572 2.51997 9.60183 2.43326 9.76873C2.35809 9.91342 2.35819 10.0857 2.43353 10.2303C2.52043 10.3971 2.81811 10.5128 3.41345 10.7444L10.1715 13.3725C10.2923 13.4195 10.3527 13.443 10.4036 13.4793C10.4487 13.5114 10.4881 13.5509 10.5203 13.596C10.5566 13.6468 10.5801 13.7073 10.6271 13.8281Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  );
}