
import LoginComponent from "./components/login";
import styles from './page.module.css'
export default function Home() {
  return (
    <div className={styles.container}>
      <LoginComponent/>
    </div>
  );
}
