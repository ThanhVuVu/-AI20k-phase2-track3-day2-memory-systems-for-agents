import json
from datasets import load_dataset

def download_and_format_hotpot(num_samples=100, output_path="data/hotpot_100.json"):
    print("🚀 Đang tải dataset từ HuggingFace (có thể mất vài phút)...")
    # Tải tập validation (thường nhỏ và sạch hơn tập train để làm benchmark)
    ds = load_dataset("hotpotqa/hotpot_qa", "fullwiki", split="validation", streaming=True)
    
    formatted_data = []
    count = 0

    for item in ds:
        if count >= num_samples:
            break
            
        # Chuyển đổi định dạng context từ HF sang format của Lab
        # HF context: {'title': ['A', 'B'], 'sentences': [['s1', 's2'], ['s3']]}
        # Lab context: [{'title': 'A', 'text': 's1 s2'}, {'title': 'B', 'text': 's3'}]
        lab_context = []
        for title, sentences in zip(item['context']['title'], item['context']['sentences']):
            lab_context.append({
                "title": title,
                "text": " ".join(sentences)
            })

        # Tạo record mới theo format yêu cầu
        record = {
            "qid": item['id'],
            "difficulty": item['level'],
            "question": item['question'],
            "gold_answer": item['answer'],
            "context": lab_context
        }
        
        formatted_data.append(record)
        count += 1
        if count % 10 == 0:
            print(f"✅ Đã xử lý {count}/{num_samples} mẫu...")

    # Lưu xuống file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=2)
    
    print(f"🎉 Hoàn thành! Đã lưu {num_samples} mẫu vào {output_path}")

if __name__ == "__main__":
    download_and_format_hotpot()
