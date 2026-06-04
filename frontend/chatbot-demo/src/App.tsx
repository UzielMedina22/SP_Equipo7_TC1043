import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ChatbotPage from "./pages/ChatbotPage";
import CustomerServicePage from "./pages/CustomerServicePage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/customer-service" element={<CustomerServicePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
