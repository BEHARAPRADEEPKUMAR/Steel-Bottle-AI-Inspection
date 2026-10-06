import { useEffect, useRef, useState } from "react";
import axios from "axios";

import {
  Activity,
  AlertCircle,
  CheckCircle2,
  CirclePlay,
  Cpu,
  FileVideo,
  Film,
  Gauge,
  Loader2,
  Play,
  RefreshCw,
  ShieldCheck,
  Upload,
  Video,
  XCircle,
} from "lucide-react";

import "./index.css";


const API_URL = "http://127.0.0.1:8000";


function App() {

  // ==========================================================
  // STATE
  // ==========================================================

  const [demoVideos, setDemoVideos] = useState([]);

  const [selectedDemo, setSelectedDemo] = useState(null);

  const [selectedFile, setSelectedFile] = useState(null);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [demoLoading, setDemoLoading] = useState(true);

  const [error, setError] = useState("");

  const fileInputRef = useRef(null);


  // ==========================================================
  // LOAD DEMO VIDEOS
  // ==========================================================

  useEffect(() => {

    const loadDemoVideos = async () => {

      try {

        const response = await axios.get(
          `${API_URL}/api/demo-videos/`
        );

        if (
          response.data &&
          response.data.success
        ) {

          setDemoVideos(
            response.data.videos || []
          );

        }

      } catch (err) {

        console.error(
          "Failed to load demo videos:",
          err
        );

        setError(
          "Unable to load predefined demo videos."
        );

      } finally {

        setDemoLoading(false);

      }

    };

    loadDemoVideos();

  }, []);


  // ==========================================================
  // SELECT DEMO VIDEO
  // ==========================================================

  const handleDemoSelect = (video) => {

    setSelectedDemo(video);

    // Clear uploaded video
    setSelectedFile(null);

    // Clear previous result
    setResult(null);

    setError("");

    // Clear file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

  };


  // ==========================================================
  // FILE SELECT
  // ==========================================================

  const handleFileChange = (event) => {

    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);

    // Clear demo selection
    setSelectedDemo(null);

    // Clear previous result
    setResult(null);

    setError("");

  };


  // ==========================================================
  // START INSPECTION
  // ==========================================================

  const handleInspection = async () => {

    if (!selectedFile && !selectedDemo) {

      setError(
        "Please upload a video or select a demo video."
      );

      return;

    }

    setLoading(true);

    setError("");

    setResult(null);


    try {

      const formData = new FormData();


      // ------------------------------------------------------
      // UPLOADED VIDEO
      // ------------------------------------------------------

      if (selectedFile) {

        formData.append(
          "video",
          selectedFile
        );

      }


      // ------------------------------------------------------
      // DEMO VIDEO
      // ------------------------------------------------------

      else if (selectedDemo) {

        formData.append(
          "demo_video",
          selectedDemo.id
        );

      }


      const response = await axios.post(
        `${API_URL}/api/inspect/`,
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },

          timeout: 0,
        }
      );


      if (
        response.data &&
        response.data.success
      ) {

        setResult(response.data);

      } else {

        setError(
          response.data?.message ||
          "Inspection failed."
        );

      }

    } catch (err) {

      console.error(
        "Inspection error:",
        err
      );

      setError(
        err.response?.data?.message ||
        err.response?.data?.error ||
        "Unable to complete inspection."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==========================================================
  // RESET
  // ==========================================================

  const handleReset = () => {

    setSelectedDemo(null);

    setSelectedFile(null);

    setResult(null);

    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

  };


  // ==========================================================
  // VIDEO URL
  // ==========================================================

  const getVideoUrl = (url) => {

    if (!url) {
      return "";
    }

    if (url.startsWith("http")) {
      return url;
    }

    return `${API_URL}${url}`;

  };


  // ==========================================================
  // CURRENT SOURCE
  // ==========================================================

  const selectedSource =
    selectedFile
      ? selectedFile.name
      : selectedDemo
        ? selectedDemo.filename
        : null;


  // ==========================================================
  // DEFECT TOTAL
  // ==========================================================

  const defectEntries =
    result?.defect_summary
      ? Object.entries(
          result.defect_summary
        )
      : [];


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="app-shell">


      {/* ====================================================
          HEADER
      ==================================================== */}

      <header className="top-header">

        <div className="brand-area">

          <div className="brand-icon">

            <Cpu size={25} />

          </div>

          <div>

            <h1>
              Steel Bottle AI Inspection
            </h1>

            <p>
              Automated manufacturing quality inspection
            </p>

          </div>

        </div>


        <div className="system-status">

          <span className="status-dot"></span>

          System Online

        </div>

      </header>


      {/* ====================================================
          MAIN
      ==================================================== */}

      <main className="main-container">


        {/* ==================================================
            HERO
        ================================================== */}

        <section className="hero-section">

          <div>

            <div className="hero-badge">

              <Activity size={14} />

              AI-POWERED QUALITY INSPECTION

            </div>


            <h2>

              Automated bottle inspection.

              <span>
                Intelligent quality decisions.
              </span>

            </h2>


            <p>

              Detect manufacturing defects using
              computer vision and frame-level analysis.

            </p>

          </div>


          <div className="hero-icon">

            <Gauge size={58} />

          </div>

        </section>


        {/* ==================================================
            PIPELINE
        ================================================== */}

        <section className="pipeline-section">


          <div className="pipeline-step">

            <div className="pipeline-icon">

              <Video size={18} />

            </div>

            <div>

              <strong>
                Video Input
              </strong>

              <span>
                Upload / Demo
              </span>

            </div>

          </div>


          <div className="pipeline-line"></div>


          <div className="pipeline-step">

            <div className="pipeline-icon">

              <Cpu size={18} />

            </div>

            <div>

              <strong>
                Bottle Detection
              </strong>

              <span>
                YOLO
              </span>

            </div>

          </div>


          <div className="pipeline-line"></div>


          <div className="pipeline-step">

            <div className="pipeline-icon">

              <ShieldCheck size={18} />

            </div>

            <div>

              <strong>
                Defect Analysis
              </strong>

              <span>
                Computer Vision
              </span>

            </div>

          </div>


          <div className="pipeline-line"></div>


          <div className="pipeline-step">

            <div className="pipeline-icon">

              <CheckCircle2 size={18} />

            </div>

            <div>

              <strong>
                Quality Decision
              </strong>

              <span>
                Accept / Reject
              </span>

            </div>

          </div>


        </section>


        {/* ==================================================
            DASHBOARD
        ================================================== */}

        <section className="dashboard-grid">


          {/* =================================================
              LEFT — INPUT
          ================================================= */}

          <div className="panel">


            <div className="panel-header">

              <div className="panel-title-icon">

                <Upload size={22} />

              </div>

              <div>

                <h3>
                  Inspection Source
                </h3>

                <p>
                  Upload your own video or select a demo
                </p>

              </div>

            </div>


            {/* ===============================================
                UPLOAD
            =============================================== */}

            <div
              className={
                selectedFile
                  ? "upload-box upload-box-selected"
                  : "upload-box"
              }

              onClick={() => {

                if (!loading) {

                  fileInputRef.current?.click();

                }

              }}
            >

              <div className="upload-icon">

                <FileVideo size={34} />

              </div>


              <h4>

                {selectedFile
                  ? "Video Selected"
                  : "Select inspection video"}

              </h4>


              <p>

                {selectedFile
                  ? selectedFile.name
                  : "Supported formats: MP4, AVI, MOV, MKV"}

              </p>


              <button
                type="button"
                className="secondary-button"

                onClick={(event) => {

                  event.stopPropagation();

                  fileInputRef.current?.click();

                }}
              >

                <Upload size={16} />

                {selectedFile
                  ? "Choose Another Video"
                  : "Choose Video"}

              </button>


              <input
                ref={fileInputRef}

                type="file"

                accept=".mp4,.avi,.mov,.mkv,video/*"

                onChange={handleFileChange}

                style={{
                  display: "none",
                }}
              />

            </div>


            {/* ===============================================
                DIVIDER
            =============================================== */}

            <div className="source-divider">

              <span>
                OR SELECT A PREDEFINED DEMO
              </span>

            </div>


            {/* ===============================================
                DEMO VIDEOS
            =============================================== */}

            <div className="demo-section">


              <div className="demo-heading">

                <div>

                  <h4>
                    Demo Videos
                  </h4>

                  <p>
                    Select a manufacturing scenario
                  </p>

                </div>


                <div className="demo-count">

                  {demoVideos.length || 0} DEMOS

                </div>

              </div>


              {demoLoading ? (

                <div className="demo-loading">

                  <Loader2
                    size={18}
                    className="spin"
                  />

                  Loading demo videos...

                </div>

              ) : demoVideos.length === 0 ? (

                <div className="demo-loading">

                  No demo videos available.

                </div>

              ) : (

                <div className="demo-grid">

                  {demoVideos.map((video) => {

                    const isSelected =
                      selectedDemo?.id === video.id;


                    return (

                      <div
                        key={video.id}

                        className={
                          isSelected
                            ? "demo-card demo-card-selected"
                            : "demo-card"
                        }

                        onClick={() =>
                          handleDemoSelect(video)
                        }
                      >


                        {/* VIDEO PREVIEW */}

                        <div className="demo-preview">

                          <video
                            src={getVideoUrl(
                              video.video_url
                            )}

                            muted

                            preload="metadata"

                            playsInline
                          />


                          {!isSelected && (

                            <div className="demo-play">

                              <Play
                                size={16}
                                fill="currentColor"
                              />

                            </div>

                          )}


                          {isSelected && (

                            <div className="selected-overlay">

                              <CheckCircle2
                                size={23}
                              />

                              SELECTED

                            </div>

                          )}

                        </div>


                        {/* INFO */}

                        <div className="demo-info">

                          <h5>
                            {video.title}
                          </h5>

                          <p>
                            {video.description}
                          </p>

                          <span className="demo-filename">

                            {video.filename}

                          </span>

                        </div>


                        {/* SELECT BUTTON */}

                        <button
                          type="button"

                          className={
                            isSelected
                              ? "demo-select-button demo-selected-button"
                              : "demo-select-button"
                          }

                          onClick={(event) => {

                            event.stopPropagation();

                            handleDemoSelect(video);

                          }}
                        >

                          {isSelected ? (

                            <>
                              <CheckCircle2
                                size={13}
                              />

                              Selected

                            </>

                          ) : (

                            <>
                              <CirclePlay
                                size={13}
                              />

                              Select Video

                            </>

                          )}

                        </button>


                      </div>

                    );

                  })}

                </div>

              )}

            </div>


            {/* ===============================================
                SELECTED SOURCE
            =============================================== */}

            {selectedSource && (

              <div className="selected-source">

                <CheckCircle2
                  size={18}
                  className="selected-source-icon"
                />

                <div>

                  <span>
                    SELECTED INSPECTION SOURCE
                  </span>

                  <strong>
                    {selectedSource}
                  </strong>

                </div>

              </div>

            )}


            {/* ===============================================
                ERROR
            =============================================== */}

            {error && (

              <div className="error-box">

                <AlertCircle
                  size={17}
                />

                <span>
                  {error}
                </span>

              </div>

            )}


            {/* ===============================================
                ONE START BUTTON
            =============================================== */}

            <button
              type="button"

              className="start-inspection-button"

              disabled={
                loading ||
                (!selectedFile &&
                  !selectedDemo)
              }

              onClick={handleInspection}
            >

              {loading ? (

                <>

                  <Loader2
                    size={19}
                    className="spin"
                  />

                  AI Inspection Running...

                </>

              ) : (

                <>

                  <Play
                    size={19}
                    fill="currentColor"
                  />

                  Start AI Inspection

                </>

              )}

            </button>


            {/* ===============================================
                RESET
            =============================================== */}

            {(selectedFile ||
              selectedDemo ||
              result) && (

              <button
                type="button"

                className="reset-button"

                onClick={handleReset}

                disabled={loading}
              >

                <RefreshCw size={13} />

                Reset Selection

              </button>

            )}

          </div>


          {/* =================================================
              RIGHT — OUTPUT
          ================================================= */}

          <div className="panel">


            <div className="panel-header">

              <div className="panel-title-icon">

                <CirclePlay size={22} />

              </div>

              <div>

                <h3>
                  Inspection Output
                </h3>

                <p>
                  AI processed manufacturing video
                </p>

              </div>

            </div>


            {/* ===============================================
                VIDEO OUTPUT
            =============================================== */}

            <div className="output-video-container">


              {result?.video_url ? (

                <video
                  className="output-video"

                  src={getVideoUrl(
                    result.video_url
                  )}

                  controls

                  playsInline

                />

              ) : (

                <div className="empty-output">

                  <div className="empty-output-icon">

                    <CirclePlay size={38} />

                  </div>

                  <h4>
                    No inspection output yet
                  </h4>

                  <p>

                    Select a demo video or upload
                    manufacturing footage and start
                    the AI inspection.

                  </p>

                </div>

              )}

            </div>


            {/* ===============================================
                SUMMARY
            =============================================== */}

            {result && (

              <>

                <div className="summary-grid">


                  {/* TOTAL */}

                  <div className="summary-card total-card">

                    <div className="summary-icon">

                      <Film size={19} />

                    </div>

                    <div>

                      <span>
                        TOTAL BOTTLES
                      </span>

                      <strong>
                        {result.total_bottles}
                      </strong>

                    </div>

                  </div>


                  {/* ACCEPTED */}

                  <div className="summary-card accepted-card">

                    <div className="summary-icon">

                      <CheckCircle2 size={19} />

                    </div>

                    <div>

                      <span>
                        ACCEPTED
                      </span>

                      <strong>
                        {result.accepted}
                      </strong>

                    </div>

                  </div>


                  {/* REJECTED */}

                  <div className="summary-card rejected-card">

                    <div className="summary-icon">

                      <XCircle size={19} />

                    </div>

                    <div>

                      <span>
                        REJECTED
                      </span>

                      <strong>
                        {result.rejected}
                      </strong>

                    </div>

                  </div>


                </div>


                {/* ===========================================
                    DEFECT ANALYSIS
                =========================================== */}

                <div className="result-section">

                  <div className="result-section-header">

                    <h4>
                      Defect Analysis
                    </h4>

                    <span>
                      DETECTED DEFECTS
                    </span>

                  </div>


                  <div className="defect-grid">

                    {defectEntries.length === 0 ? (

                      <div className="no-defects">

                        <CheckCircle2
                          size={16}
                        />

                        No defects detected

                      </div>

                    ) : (

                      defectEntries.map(
                        ([defect, count]) => (

                          <div
                            className="defect-card"
                            key={defect}
                          >

                            <div className="defect-card-icon">

                              <AlertCircle
                                size={16}
                              />

                            </div>

                            <div>

                              <strong>
                                {defect.replace(
                                  /_/g,
                                  " "
                                )}
                              </strong>

                              <span>
                                {count} bottle
                                {count !== 1
                                  ? "s"
                                  : ""}
                              </span>

                            </div>

                          </div>

                        )
                      )

                    )}

                  </div>

                </div>


                {/* ===========================================
                    BOTTLE RESULTS
                =========================================== */}

                <div className="result-section">

                  <div className="result-section-header">

                    <h4>
                      Bottle Inspection Results
                    </h4>

                    <span>
                      QUALITY DECISIONS
                    </span>

                  </div>


                  <div className="bottle-results">


                    {result.results?.map(
                      (item, index) => {

                        const isRejected =
                          item.status ===
                          "REJECTED";


                        return (

                          <div
                            key={index}

                            className={
                              isRejected
                                ? "bottle-result bottle-rejected"
                                : "bottle-result bottle-good"
                            }
                          >

                            <div className="bottle-status-icon">

                              {isRejected ? (

                                <XCircle
                                  size={18}
                                />

                              ) : (

                                <CheckCircle2
                                  size={18}
                                />

                              )}

                            </div>


                            <div className="bottle-result-info">

                              <strong>

                                {isRejected
                                  ? "REJECTED"
                                  : "ACCEPTED"}

                              </strong>


                              <span>

                                {isRejected

                                  ? (
                                    item.defect ||
                                    "Defect detected"
                                  )

                                  : "GOOD"}

                              </span>

                            </div>


                            {isRejected &&
                              item.severity && (

                              <div className="severity-badge">

                                {item.severity}

                              </div>

                            )}

                          </div>

                        );

                      }
                    )}

                  </div>

                </div>

              </>

            )}

          </div>

        </section>


        {/* ==================================================
            FOOTER
        ================================================== */}

        <footer className="app-footer">

          <div>

            <ShieldCheck size={13} />

            AI-assisted manufacturing inspection

          </div>


          <div>

            YOLO • Computer Vision • Django • React

          </div>

        </footer>


      </main>

    </div>

  );

}


export default App;