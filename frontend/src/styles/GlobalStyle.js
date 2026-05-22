import { createGlobalStyle } from "styled-components";

export const GlobalStyle = createGlobalStyle`
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        list-style: none;
        font-family: Geneva, Verdana, sans-serif;
        color: white;
    }

    html, body, #root {
        background: #0A110C;
        height: 100%;
        width: 100%;
    }
`;
