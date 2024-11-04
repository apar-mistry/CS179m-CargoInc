"use client";
import React, { useEffect, useState } from "react";
import { Button, Container, Typography, Box } from "@mui/material";
import { useRouter } from "next/navigation";
import axios from "axios";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
const MainPage = () => {
  const [username, setUsername] = useState("");
  const router = useRouter();

  useEffect(() => {
    const storedUsername = sessionStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    } else {
      router.push("/"); // Redirect to login if no username is found
    }
  }, [router]);

  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:5000/api/log_logout", {
        username: username,
      });
      sessionStorage.setItem("username", "");
      router.push("/"); // Redirect to the main page after login
    } catch (error) {
      console.error("Error logging in:", error);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: "var(--steel-gray)" }}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <img
              src="/logo.png" // Replace with your image path or URL
              alt="Logo"
              style={{ width: "40px", height: "40px" }} // Adjust size as needed
            />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Welcome {sessionStorage.getItem("username")}!
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
};

export default MainPage;
