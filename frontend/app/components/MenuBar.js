import { AppBar, Toolbar, Button, IconButton, Typography } from "@mui/material";
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

const MenuBar = () => {
  const router = useRouter();
  const [showButton, setShowButton] = useState(false);

  useEffect(() => {
    // Check if certain items are present in sessionStorage
    const item1 = sessionStorage.getItem("route");
    const item2 = sessionStorage.getItem("operation");
    if (item1 && item2) {
      setShowButton(true);
    }
  }, []);
  const username = sessionStorage.getItem("username");
  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:5000/api/log_logout", { username });
      sessionStorage.setItem("username", "");
      router.push("/"); // Redirect to the login page after logout
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: "var(--steel-gray)" }}>
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="logo"
          sx={{ mr: 2 }}
        >
          <img
            src="/crane.png" // Replace with your image path or URL
            alt="Logo"
            style={{ width: "40px", height: "40px" }}
          />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Welcome, {username}!
        </Typography>
        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, justifyContent: "center" }}
        >
          {sessionStorage.getItem("operation")}
        </Typography>
        {showButton && (
          <Button color="inherit" onClick={() =>{
            sessionStorage.removeItem("route")
            sessionStorage.removeItem("operation")
            router.push("/main")}}>
            Home
          </Button>
        )}
        <Button color="inherit" onClick={handleLogout}>
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
};
export default MenuBar;
