"use client";
import React, { useEffect, useState } from "react";
import {
  Button,
  Container,
  Typography,
  Box,
  Grid,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { useRouter } from "next/navigation";
import axios from "axios";
import MenuBar from "../components/MenuBar";
import { set } from "express/lib/application";

const MainPage = () => {
  const [username, setUsername] = useState("");
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [operation, setOperation] = useState("");
  const [routeName, setRoute] = useState("");

  const router = useRouter();

  useEffect(() => {
    const storedUsername = sessionStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    } else {
      router.push("/"); // Redirect to login if no username is found
    }
  }, [router]);


  const handleOpenDialog = (operationType, route) => {
    setOperation(operationType);
    sessionStorage.setItem("operation", operationType);
    sessionStorage.setItem("route", route);
    setOpen(true);
  };

  const handleCloseDialog = () => {
    setOpen(false);
    setFile(null); // Clear file input on close
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "text/plain") {
      setFile(selectedFile);
    } else {
      alert("Please select a .txt file.");
    }
  };

  const handleUpload = async () => {
    if (file) {
      try {
        const formData = new FormData();
        formData.append("file", file);
  
        // Send the file to the backend
        const response = await axios.post("http://127.0.0.1:5000/api/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
  
        console.log("File uploaded successfully:", response.data);
        alert("File uploaded successfully");
  
        // Navigate to the grid display page after successful upload
        router.push(sessionStorage.getItem("route"));
        handleCloseDialog(); // Close dialog after successful upload
      } catch (error) {
        console.error("Error uploading file:", error);
        alert("Error uploading file");
      }
    } else {
      alert("Please select a .txt file.");
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <MenuBar/>

      <Container maxWidth="md" style={{ marginTop: "50px" }}>
        <Grid container direction="column" alignItems="center" spacing={3}>
          <Grid item>
            <Typography variant="h4" component="h1" align="center">
              Which operation would you like to complete?
            </Typography>
          </Grid>

          <Grid item>
            <img
              src="/logo.png" // Replace with your logo path
              alt="Logo"
              style={{ width: "200px", height: "auto" }}
            />
          </Grid>

          <Grid item container justifyContent="center" spacing={2}>
            <Grid item>
              <Button
                variant="contained"
                size="large"
                onClick={() => handleOpenDialog("Balancing", "/balance")}
                sx={{ backgroundColor: "var(--dock-blue)" }}
              >
                Balance
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                size="large"
                onClick={() => handleOpenDialog("Load/Unload", "load_unload")}
                sx={{ backgroundColor: "var(--safety-orange)" }}
              >
                Load/Unload
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Container>

      <Dialog open={open} onClose={handleCloseDialog}>
        <DialogTitle>Upload File for {operation}</DialogTitle>
        <DialogContent>
          <input type="file" accept=".txt" onChange={handleFileChange} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleUpload} color="primary">
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MainPage;