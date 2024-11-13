// app/grid-display/page.js
"use client";
import GridDisplay from "../components/GridDisplay";
import MenuBar from "../components/MenuBar";
export default function DisplayPage() {
  return (
    <div>
      <MenuBar />
      <GridDisplay />
    </div>
  );
}
