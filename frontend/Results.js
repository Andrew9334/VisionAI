import React from "react";

const Results = ({ data }) => {
  if (!data || !data.results) {
    return <p>Загрузка предсказаний...</p>;
  }

  const { yolo, tensorflow, clip, final_class, final_confidence } = data;

  return (
    <div className="results-container">
      <h2>Результаты предсказания</h2>
      <p><strong>Файл:</strong> {data.file}</p>

      {/* YOLO */}
      <div className="result-card">
        <h3>YOLO</h3>
        <p><strong>Класс:</strong> {yolo.class}</p>
        <p><strong>Confidence:</strong> {yolo.confidence.toFixed(2)}</p>
      </div>

      {/* TensorFlow */}
      <div className="result-card">
        <h3>TensorFlow</h3>
        <p><strong>Класс:</strong> {tensorflow.class}</p>
        <p><strong>Confidence:</strong> {tensorflow.confidence.toFixed(2)}</p>
      </div>

      {/* CLIP */}
      <div className="result-card">
        <h3>CLIP</h3>
        <p><strong>Класс:</strong> {clip.class}</p>
        <p><strong>Confidence:</strong> {clip.confidence.toFixed(2)}</p>
      </div>

      {/* Финальный класс */}
      {final_class && (
        <div className="result-card final">
          <h3>🔥 Итоговый класс</h3>
          <p><strong>{final_class}</strong> (Confidence: {final_confidence.toFixed(2)})</p>
        </div>
      )}
    </div>
  );
};

export default Results;
