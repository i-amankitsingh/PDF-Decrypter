import React, { useState } from "react";
import axios from "axios";

const PDFDecryption = () => {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [password, setPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [decryptedPdfUrl, setDecryptedPdfUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPdfFile(e.target.files[0]);
    }
  };

  const handleDecrypt = async () => {
    if (!pdfFile || !password) return;

    setLoading(true);
    setError(null);
    setDecryptedPdfUrl(null);

    const formData = new FormData();
    formData.append("file", pdfFile);
    formData.append("password", password);

    try {
      const response = await axios.post(
        "http://localhost:5000/upload_pdf",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          responseType: "blob", // Important to handle file download
        }
      );

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      console.log("res ", response)
      setDecryptedPdfUrl(url);
    } catch (err) {
      setError("Failed to decrypt PDF. Please check the password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">PDF Decryptor</h1>

      <input
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        className="mb-4 border p-2 w-full"
      />
      <input
        type="password"
        placeholder="Enter PDF Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="mb-4 border p-2 w-full"
      />

      <button
        onClick={handleDecrypt}
        disabled={loading}
        className="bg-blue-500 text-white p-2 rounded-md w-full"
      >
        {loading ? "Decrypting..." : "Decrypt PDF"}
      </button>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {decryptedPdfUrl && (
        <div className="mt-4">
          <a
            href={decryptedPdfUrl}
            download="Unlocked_PDF.pdf"
            className="bg-green-500 text-white p-2 rounded-md"
          >
            Download Decrypted PDF
          </a>
        </div>
      )}
    </div>
  );
};

export default PDFDecryption;
