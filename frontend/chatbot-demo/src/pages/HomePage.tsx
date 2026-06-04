import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-5xl font-bold">IKEA-Bot Demo</h1>
      <p className="text-2xl p-12">Escoge la vista a la que deseas acceder.</p>
      <div className="inline-flex gap-8">
        <button className="btn-1 bg-sky-300" onClick={() => navigate("/chatbot")}>
          <p>Vista de usuario (chatbot)</p>
        </button>
        <button className="btn-1 bg-amber-300" onClick={() => navigate("/customer-service")}>
          <p>Vista de servicio al cliente</p>
        </button>
      </div>
    </div>
  );
}