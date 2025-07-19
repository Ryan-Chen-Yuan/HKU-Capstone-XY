# Zhiji AI Assistant (知己AI助手)

AI-Powered Chatbot for Mental Health.

## Quick Start

### Back-end

1. Requirement

- Python 3.11+

- OpenAI API key (for demonstration purposes, you can use the temporary key in /server/.env.example, but this key will expire in the future)

2. Install dependencies

```bash
cd server
pip install -r requirements.txt
```

3. model download

run download.ipynb

4. Configure environment variables

Copy the environment variable example file and configure it:

```bash
cp .env .env
```

5. Start the server

```bash
python start.py
```

The server will run on http://localhost:5858 by default.

### WeChat Miniprogram

1. Requirement

- IDE [WeChat developer tools WeChat devtools](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)

- Miniprogram AppID (For demonstration purposes, you can use the temporary AppID in /miniprogram/project.config.json)

2. Run the project

- Enable the "Do not verify legal domain name" option (otherwise you cannot access the local test port <http://localhost:5858>)

- Click the "Compile" button in WeChat developer tools

- Wait for the compilation to complete and you can experience it

If you encounter any problems, feel free to contact:

- Chen Yuan (<ryan.chenyuan@connect.hku.hk>)
- Xu Hanlin (<hallymxu@gmail.com>)
- Yu Yitao (<yitao_yu2024@connect.hku.hk>)
- Su Yingcheng (<suyingc@connect.hku.hk>)

