
export default function Chatbot({ handleClose }: { handleClose: () => void }) {
  return (
    <div className="chat-panel bg-white rounded-lg shadow-lg max-w-120 h-100">
      <div className="w-full chat-panel-header flex justify-between items-center mb-4">
        <h2 className="text-white text-xl font-semibold">
            IKEA-Bot
        </h2>
        <button onClick={handleClose} className="text-white">
          <svg width="24" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <div className="mb-4">
        <p className="text-gray-700">¡Hola! Soy IKEA-Bot. ¿En qué puedo ayudarte?</p>
      </div>
    </div>
  );
}