from transformers import pipeline
import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os
import json
# Load a local summarization pipeline
# Uses Qwen2.5-3B-Instruct (great for local instruction execution & summarization)


def download_qwen():
    # Target local folder
    local_folder = "./models/Qwen2.5-3B-Instruct"

    # Download model directly into the specified path
    snapshot_download(
        repo_id="Qwen/Qwen2.5-3B-Instruct",
        local_dir=local_folder,
        local_dir_use_symlinks=False  # Downloads actual files instead of symlinks
    )

    print(f"Model successfully saved to {local_folder}")

def load_offline_from_weight(model_path="./models/Qwen2.5-3B-Instruct"):
    local_model_path = model_path

    # 1. Load Tokenizer & Model strictly offline
    tokenizer = AutoTokenizer.from_pretrained(
        local_model_path, 
        local_files_only=True,
        clean_up_tokenization_spaces=False
    )

    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,
        dtype=torch.bfloat16,  # Replaces deprecated 'torch_dtype'
        device_map="auto",
        local_files_only=True
    )

    # 2. Setup pipeline
    summarizer = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    )
    print("Load offline Qwen weight successfullly")
    return summarizer
def load_Qwen_by_API():
    model_name = "Qwen/Qwen2.5-3B-Instruct"

    summarizer = pipeline(
        "text-generation",
        model=model_name,
        model_kwargs={"torch_dtype": torch.bfloat16}, # Use torch.float16 if GPU doesn't support bfloat16
        device_map="auto"                              # Automatically handles CPU/GPU placement
    )
    return summarizer


def summarize_text(summarizer,text: str, max_new_tokens: int = 1000) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes text and then translate the summary to vietnamese:"},
        {"role": "user", "content": f"Please extract importance information of the following text:\n\n{text}"}
    ]
    
    prompt = summarizer.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    outputs = summarizer(
        prompt, 
        max_new_tokens=max_new_tokens, 
        do_sample=False
    )
    
    # Extract generated response text
    generated_text = outputs[0]["generated_text"]
    response = generated_text[len(prompt):].strip()
    return response

# Example Usage
content = """
**Date:** May 20, 2026  
**URL:** https://www.torm.com/news/company-announcements/company-announcements-details/2026/TORM-plc-capital-increase-in-connection-with-exercise-of-Restricted-Share-Units-as-part-of-TORMs-incentive-program-2ea0cb7bf/default.aspx

Philippines, Manila:+63 2 8988 6500

Philippines, Cebu:+63 32 266 5534

India, Mumbai:+91 (022) 6640 7200

India, New Delhi:+91 (011) 6640 7201

United Kingdom:+44 203 713 4560

TORM plc capital increase in connection with exercise of Restricted Share Units as part of TORM’s incentive program

TORM plc (Nasdaq: TRMD or TRMD A) has increased its share capital by 215,635 A-shares (corresponding to a nominal value of USD 2.156,35) as a result of the exercise of a corresponding number of Restricted Share Units (“RSUs”). A total of 14,206 new shares is subscribed for in cash at DKK 0.07 per A-share, 85,067 shares are subscribed for in cash at DKK 131.80 and 116,362 new shares are subscribed for in cash at DKK 144.40.

Transfer restrictions may apply in certain jurisdictions outside Denmark, including applicable US securities laws. The capital increase is carried out without any pre-emption rights for existing shareholders or others.

The new shares (i) are ordinary shares without any special rights and are negotiable instruments, (ii) give the right to dividends and other rights in relation to TORM as of the date of issuance and (iii) are expected to be admitted to trading and official listing on Nasdaq Copenhagen as soon as possible.

After the capital increase, TORM’s share capital totals to USD 1,023,389.74 divided into 102,338,974 A-shares with a nominal value of USD 0.01 each. Each A-share carries one vote.

Mikael Bo Larsen, Head of Investor Relations

TORM is one of the world’s leading carriers of refined oil products. TORM operates a fleet of product tanker vessels with a strong commitment to safety. environmental responsibility and customer service. TORM was founded in 1889 and conducts business worldwide. TORM’s shares are listed on Nasdaq in Copenhagen and on Nasdaq in New York (ticker: TRMD A and TRMD. ISIN: GB00BZ3CNK81). For further information, please visit www.torm.com.

Safe Harbor Statement as to the Future

Matters discussed in this release may constitute forward-looking statements. The Private Securities Litigation Reform Act of 1995 provides safe harbor protections for forward-looking statements in order to encourage companies to provide prospective information about their business. Forward-looking statements reflect our current views with respect to future events and financial performance and may include statements concerning plans, objectives, goals, strategies, future events or performance, and underlying assumptions and other statements, which are statements other than statements of historical facts. The Company desires to take advantage of the safe harbor provisions of the Private Securities Litigation Reform Act of 1995 and is including this cautionary statement in connection with this safe harbor legislation. Words such as, but not limited to, “expects,” “anticipates,” “intends,” “plans,” “believes,” “estimates,” “targets,” “projects,” “forecasts,” “potential,” “continue,” “possible,” “likely,” “may,” “could,” “should” and similar expressions or phrases may identify forward-looking statements.

The forward-looking statements in this release are based upon various assumptions, many of which are, in turn, based upon further assumptions, including without limitation, management’s examination of historical operating trends, data contained in our records and other data available from third parties. Although the Company believes that these assumptions were reasonable when made, because these assumptions are inherently subject to significant uncertainties and contingencies that are difficult or impossible to predict and are beyond our control, the Company cannot guarantee that it will achieve or accomplish these expectations, beliefs, or projections.

Important factors that, in our view, could cause actual results to differ materially from those discussed in the forward-looking statements include, but are not limited to, our future operating or financial results; changes in governmental rules and regulations or actions taken by regulatory authorities; inflationary pressure and central bank policies intended to combat overall inflation and rising interest rates and foreign exchange rates; general domestic and international political conditions or events, including “trade wars” and the war between Russia and Ukraine, the developments in the Middle East, including the war in Israel and the Gaza Strip, and the conflict regarding the Houthis’ attacks in the Red Sea; international sanctions against Russian oil and oil products; changes in economic and competitive conditions affecting our business, including market fluctuations in charter rates and charterers’ abilities to perform under existing time charters; changes in the supply and demand for vessels comparable to ours and the number of newbuildings under construction; the highly cyclical nature of the industry that we operate in; the loss of a large customer or significant business relationship; changes in worldwide oil production and consumption and storage; risks associated with any future vessel construction; our expectations regarding the availability of vessel acquisitions and our ability to complete acquisition transactions planned; availability of skilled crew members other employees and the related labor costs; work stoppages or other labor disruptions by our employees or the employees of other companies in related industries; effects of new products and new technology in our industry; new environmental regulations and restrictions; the impact of an interruption in or failure of our information technology and communications systems, including the impact of cyber-attacks, upon our ability to operate; potential conflicts of interest involving members of our Board of Directors and Senior Management; the failure of counterparties to fully perform their contracts with us; changes in credit risk with respect to our counterparties on contracts; adequacy of insurance coverage; our ability to obtain indemnities from customers; changes in laws, treaties or regulations; our incorporation under the laws of England and Wales and the different rights to relief that may be available compared to other countries, including the United States; government requisition of our vessels during a period of war or emergency; the arrest of our vessels by maritime claimants; any further changes in U.S. trade policy that could trigger retaliatory actions by the affected countries; the impact of the U.S. presidential and congressional election results affecting the economy, future government laws and regulations and trade policy matters, such as the imposition of tariffs and other import restrictions; potential disruption of shipping routes due to accidents, climate-related incidents, adverse weather and natural disasters, environmental factors, political events, public health threats, acts by terrorists or acts of piracy on ocean-going vessels; damage to storage and receiving facilities; potential liability from future litigation and potential costs due to environmental damage and vessel collisions; and the length and number of off-hire periods and dependence on third-party managers.

In the light of these risks and uncertainties, undue reliance should not be placed on forward-looking statements contained in this release because they are statements about events that are not certain to occur as described or at all. These forward-looking statements are not guarantees of our future performance, and actual results and future developments may vary materially from those projected in the forward-looking statements.

Except to the extent required by applicable law or regulation, the Company undertakes no obligation to release publicly any revisions or updates to these forward-looking statements to reflect events or circumstances after the date of this release or to reflect the occurrence of unanticipated events. Please see TORM’s filings with the U.S. Securities and Exchange Commission for a more complete discussion of certain of these and other risks and uncertainties. The information set forth herein speaks only as of the date hereof, and the Company disclaims any intention or obligation to update any forward-looking statements as a result of developments occurring after the date of this communication.
"""
def get_contents_from_json(file_path: str) -> list[str]:
    """
    Reads a JSON file and extracts all text found under the 'content' key.
    Returns a list of strings containing the content text.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract 'content' from each item if the key exists
    contents = [item["content"] for item in data if "content" in item]
    return contents
def add_summaries_and_save(file_path: str, output_path: str, summaries: list[str] | str) -> None:
    """
    Reads a JSON file, adds the provided summary text to 'summary_content' key, 
    and saves the updated data to output_path.
    
    :param file_path: Path to input JSON file.
    :param output_path: Path to save updated JSON file.
    :param summaries: A list of summary strings (one per item) OR a single summary string.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle case where a list of summaries is passed
    if isinstance(summaries, list):
        for item, summary_text in zip(data, summaries):
            item["summary_content"] = summary_text
            
    # Handle case where a single summary string is passed for all items
    else:
        for item in data:
            item["summary_content"] = summaries

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved updated file to: {output_path}")

def main():
    path="./models/Qwen2.5-3B-Instruct"
    # if not os.path.exists(path):
    #     print("Model path not found. Starting download...")
    #     download_qwen()

    contents = get_contents_from_json("result/torm_articles.json")
    summarizer=load_offline_from_weight(model_path="./models/Qwen2.5-3B-Instruct")
    summaries_list = [summarize_text(summarizer, text) for text in contents]
    #summary = summarize_text(summarizer,content)
    add_summaries_and_save(
        file_path="result/torm_articles.json",
        output_path="result/torm_articles.json",
        summaries=summaries_list
    )

    print("Summary:\n", summary)

if __name__ == "__main__":
    main()