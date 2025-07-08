import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Shop from "./pages/Shop";
import Profile from "./pages/Profile";
import Cart from "./pages/Cart";
import Shipping from "./pages/Shipping";
import Order from "./pages/Order";
import Payment from "./pages/Payment";
import Review from "./pages/Review";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/shop" element={<Shop />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/order" element={<Order />} />
         <Route path="/shipping" element={<Shipping/>} />
         <Route path="/payment" element={<Payment />} />
         <Route path="/review" element={<Review />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  );
}

export default App;
