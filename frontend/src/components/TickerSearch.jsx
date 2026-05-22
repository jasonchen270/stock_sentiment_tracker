import React, { useState, useRef } from "react";
import axios from "axios";
import styled from "styled-components";
import { format, parseISO } from "date-fns";
import { Layout } from "../styles/Layout";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { toast } from "react-hot-toast";

function TickerSearch() {
  const [sentimentData, setSentimentData] = useState([]);
  const [inputTicker, setInputTicker] = useState("");
  const [priceData, setPriceData] = useState([]);
  const submitButtonRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const submitButton = submitButtonRef.current;
    submitButton.disabled = true;
    submitButton.classList.add("btn--running");

    const inputTicker = e.target.elements.ticker.value;

    setSentimentData([]);
    setPriceData([]);

    try {
      setInputTicker(inputTicker);

      const response = await axios.post(
        "http://localhost:5000/start-individual-scraper",
        {
          ticker: inputTicker,
        }
      );

      console.log(response.data.message);
      setPriceData(response.data.prices);
      setSentimentData(response.data.sentiment_data);
    } catch (error) {
      console.log(error);
      toast.error("Failed to load data. Please try again.");
    } finally {
      submitButton.disabled = false;
      submitButton.classList.remove("btn--running");
    }
  };

  const pastSevenDatesFromPriceData = priceData
    .slice(0, 7)
    .reverse()
    .map((data) => data[1]);

  const filteredSentimentData = pastSevenDatesFromPriceData.map((date) => {
    const sentimentDataForDate = sentimentData[inputTicker]?.[date];
    return {
      ticker: inputTicker,
      date,
      sentimentScore: sentimentDataForDate || "-",
    };
  });

  const filteredPriceData = pastSevenDatesFromPriceData.map((date) => {
    const priceDataForDate = priceData.find((data) => data[1] === date);
    return {
      ticker: inputTicker,
      date,
      price: priceDataForDate?.[2]
        ? parseFloat(priceDataForDate[2].replace(",", ""))
        : null,
    };
  });

  return (
    <Layout>
      <StyledContainer>
        <div className="search-container">
          <h1>Lookup Stock</h1>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              name="ticker"
              autoComplete="off"
              placeholder="Enter Ticker"
            />
            <button
              type="submit"
              className="loader-button"
              ref={submitButtonRef}
            >
              <span className="btn__text">Submit</span>
              <div className="loader"></div>
            </button>
          </form>
        </div>

        <div className="sentiment-chart">
          <h1>Sentiment Score History</h1>
          {filteredSentimentData.length > 0 && (
            <ResponsiveContainer>
              <LineChart data={filteredSentimentData}>
                <CartesianGrid vertical={false} horizontal={false} />
                <XAxis
                  dataKey="date"
                  tickLine={false}
                  axisLine={{ stroke: 'white' }}
                  tick={{ fill: 'white' }}
                  tickFormatter={(date) => {
                    return format(parseISO(date), "MMM, d");
                  }}
                  padding={{ left: 50, right: 50 }}
                  height={30}
                />
                <YAxis
                  tickLine={false}
                  domain={["auto", "auto"]}
                  axisLine={{ stroke: 'white' }}
                  tick={{ fill: 'white' }}
                  tickFormatter={(value) => value.toFixed(3)}
                  padding={{ top: 50, bottom: 50 }}
                  width={100}
                />
                <Tooltip content={SentimentTooltip} />
                <Line
                  type="monotone"
                  dataKey="sentimentScore"
                  name="Sentiment Score"
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="price-chart">
          <h1>Stock Price History</h1>
          {filteredPriceData.length > 0 && (
            <ResponsiveContainer>
              <LineChart data={filteredPriceData}>
                <CartesianGrid vertical={false} horizontal={false} />
                <XAxis
                  dataKey="date"
                  tickLine={false}
                  axisLine={{ stroke: 'white' }}
                  tick={{ fill: 'white' }}
                  tickFormatter={(date) => {
                    return format(parseISO(date), "MMM, d");
                  }}
                  padding={{ left: 50, right: 50 }}
                  height={30}
                />
                <YAxis
                  tickLine={false}
                  axisLine={{ stroke: 'white' }}
                  domain={["auto", "auto"]}
                  padding={{ top: 50, bottom: 50 }}
                  tick={{ fill: 'white' }}
                  tickFormatter={(value) => `$${value.toFixed(2)}`}
                  width={100}
                />
                <Tooltip content={PriceTooltip} />
                <Line type="monotone" dataKey="price" name="Stock Price" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </StyledContainer>
    </Layout>
  );
}

function SentimentTooltip({ active, payload, label }) {
  if (active) {
    const score = payload[0].value;
    return (
      <div className="tooltip">
        <h4>{format(parseISO(label), "eeee, d MMM, yyyy")}</h4>
        <p>{`Sentiment Score: ${
          typeof score === "number" ? score.toFixed(4) : score
        }`}</p>
      </div>
    );
  }
}

function PriceTooltip({ active, payload, label }) {
  if (active) {
    return (
      <div className="tooltip">
        <h4>{format(parseISO(label), "eeee, d MMM, yyyy")}</h4>
        <p>{`Stock Price: $${payload[0].value.toFixed(2)}`}</p>
      </div>
    );
  }
}

const StyledContainer = styled.div`
  display: flex;
  width: 100%;
  flex-direction: row;
  align-items: center;
  height: 500px;

  @media (max-width: 768px) {
    flex-direction: column;
    height: 100%;
  }

  .search-container {
    flex: 0.5;
    display: flex;
    justify-content: center;
    margin: 30px;
    flex-direction: column;
    align-items: flex-start;

    h1 {
      font-size: 1.5rem;
      align-self: flex-start;
      margin-bottom: 10px;
      margin-left: 100px;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 10px;
      width: 50%;
      margin-left: 100px;

      input {
        border-radius: 24px;
        height: 48px;
        padding-left: 25px;
        font-size: 1rem;
        border: none;
        border: 2px solid;
        background-color: #0a110c;
      }

      input:focus {
        outline: none;
      }

      input:focus::placeholder {
        color: transparent;
      }

      .loader-button {
        height: 48px;
        border: 2px solid;
        border-radius: 24px;
        font-family: inherit;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        background-color: DarkSlateGrey;

        .btn__text {
          font-size: 1rem;
          font-weight: 600;
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
        }

        &.btn--running {
          cursor: default;

          .btn__text {
            visibility: hidden;
          }

          .loader {
            visibility: visible;
          }
        }

        .loader {
          width: 30px;
          height: 30px;
          border: 5px solid;
          border-top-color: #009578;
          border-radius: 50%;
          animation: loading 0.75s ease infinite;
          visibility: hidden;
        }

        @keyframes loading {
          from {
            transform: rotate(0turn);
          }
          to {
            transform: rotate(1turn);
          }
        }
      }
    }
  }

  .sentiment-chart {
    flex: 1;
    display: flex;
    flex-direction: column;
    border: 2px solid;
    height: 500px;
    border-radius: 10px;
    padding: 20px;
    margin: 30px;
    padding-top: 0;
  }

  .price-chart {
    flex: 1;
    display: flex;
    flex-direction: column;
    border: 2px solid;
    height: 500px;
    border-radius: 10px;
    padding: 20px;
    margin: 30px;
    padding-top: 0;
  }

  .tooltip {
    background-color: DarkSlateGrey;
    border-radius: 10px;
    padding: 1rem;
    text-align: left;

    h4 {
      margin-bottom: 10px;
    }
  }
`;

export default TickerSearch;
