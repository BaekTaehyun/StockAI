
import re

def test_parsing_logic():
    print("Testing Outlook Parsing Logic...")

    # Sample response from Gemini (based on OUTLOOK_GENERATION_PROMPT)
    # Case 1: Standard format (already tested, but good to keep)
    result_text_standard = """
1. 투자의견: 분할매수 (신뢰도: 75점)
2. 핵심 논리 (3줄 요약):
   - [미국연동]: 반도체 섹터 강세로 인한 커플링 기대
   - [수급/테마]: 외국인 순매수 유입 지속
   - [기술적]: 20일선 지지 확인 및 골든크로스 임박
3. 매매 시나리오:
   - 진입: 75,000원 (근거: 20일선 지지)
   - 목표: 82,000원 (근거: 전고점 저항)
   - 손절: 72,000원 (근거: 60일선 이탈)
4. 상세 분석:
   미국 시장의 반도체 강세가 국내 시장에도 긍정적인 영향을 미칠 것으로 예상됩니다.
   특히 외국인 수급이 개선되고 있어 추가 상승 여력이 충분합니다.
    """

    # Case 2: Inline content (The issue we are reproducing)
    result_text_inline = """
1. 투자의견: 매수 (신뢰도: 80점)
2. 핵심 논리 (3줄 요약): - [실적]: 3분기 호실적 기록
   - [모멘텀]: 신규 수주 기대감
3. 매매 시나리오: - 진입: 10,000원
   - 목표: 12,000원
   - 손절: 9,000원
4. 상세 분석: 긍정적인 흐름이 예상됩니다.
    """

    for i, result_text in enumerate([result_text_standard, result_text_inline]):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Input Text:\n{result_text}\n")

        # --- Copy of the current logic in gemini_service.py ---
        # 1. 초기값 설정
        parsed_data = {
            "recommendation": "중립",
            "confidence": 0,
            "key_logic": "",         
            "trading_scenario_raw": "", 
            "detailed_analysis": "", 
            "price_strategy": {      
                "entry": "",
                "target": "",
                "stop_loss": ""
            }
        }

        lines = result_text.strip().split('\n')
        current_section = None
        
        # 섹션별 버퍼
        logic_buffer = []
        scenario_buffer = []
        analysis_buffer = []

        for line in lines:
            line = line.strip()
            if not line: continue

            # ====================================================
            # [섹션 감지 로직]
            # ====================================================
            if line.startswith("1.") or "투자의견" in line:
                current_section = "recommendation_section"
                
                if "강력매수" in line: parsed_data["recommendation"] = "강력매수"
                elif "분할매수" in line: parsed_data["recommendation"] = "분할매수"
                elif "매수" in line: parsed_data["recommendation"] = "매수"
                elif "매도" in line: parsed_data["recommendation"] = "매도"
                elif "관망" in line: parsed_data["recommendation"] = "관망"
                
                conf_match = re.search(r'신뢰도[:\s]*(\d+)', line)
                if conf_match:
                    parsed_data["confidence"] = int(conf_match.group(1))

            elif line.startswith("2.") or "핵심 논리" in line:
                current_section = "key_logic"
                # [FIX] 같은 라인에 내용이 있는 경우 처리
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        content = parts[1].strip()
                        if content:
                            logic_buffer.append(content)
                
            elif line.startswith("3.") or "매매 시나리오" in line:
                current_section = "trading_scenario"
                # [FIX] 같은 라인에 내용이 있는 경우 처리
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        content = parts[1].strip()
                        if content:
                            scenario_buffer.append(content)
                            # 가격 전략 파싱 시도
                            if ":" in content:
                                try:
                                    key_part, value_part = content.split(":", 1)
                                    key_clean = key_part.replace("-", "").strip()
                                    value_clean = value_part.strip()
                                    
                                    if "진입" in key_clean:
                                        parsed_data["price_strategy"]["entry"] = value_clean
                                    elif "목표" in key_clean:
                                        parsed_data["price_strategy"]["target"] = value_clean
                                    elif "손절" in key_clean:
                                        parsed_data["price_strategy"]["stop_loss"] = value_clean
                                except:
                                    pass
                
            elif line.startswith("4.") or "상세 분석" in line:
                current_section = "detailed_analysis"
                # [FIX] 같은 라인에 내용이 있는 경우 처리
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        content = parts[1].strip()
                        if content:
                            analysis_buffer.append(content)

            # ====================================================
            # [섹션별 내용 수집]
            # ====================================================
            else:
                if current_section == "key_logic":
                    logic_buffer.append(line)
                    
                elif current_section == "trading_scenario":
                    scenario_buffer.append(line)
                    
                    if ":" in line:
                        key_part, value_part = line.split(":", 1)
                        key_clean = key_part.replace("-", "").strip()
                        value_clean = value_part.strip()
                        
                        if "진입" in key_clean:
                            parsed_data["price_strategy"]["entry"] = value_clean
                        elif "목표" in key_clean:
                            parsed_data["price_strategy"]["target"] = value_clean
                        elif "손절" in key_clean:
                            parsed_data["price_strategy"]["stop_loss"] = value_clean

                elif current_section == "detailed_analysis":
                    analysis_buffer.append(line)

        # --- FIXED CODE ---
        parsed_data["key_logic"] = "\n".join(logic_buffer)
        parsed_data["trading_scenario_raw"] = "\n".join(scenario_buffer)
        parsed_data["detailed_analysis"] = "\n".join(analysis_buffer)
        # ------------------

        result = {
            'recommendation': parsed_data['recommendation'],
            'confidence': parsed_data['confidence'],
            'key_logic': parsed_data['key_logic'],
            'price_strategy': parsed_data['price_strategy'],
            'trading_scenario': parsed_data['trading_scenario_raw'],
            'detailed_analysis': parsed_data['detailed_analysis'] if parsed_data['detailed_analysis'] else result_text,
            'raw_response': result_text
        }

        print("-" * 30)
        print("Parsed Result:")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Trading Scenario (Raw): '{result['trading_scenario']}'")
        print(f"Key Logic: '{result['key_logic']}'")
        print(f"Detailed Analysis: '{result['detailed_analysis']}'")
        print("-" * 30)

        if i == 1: # Check failure for inline case
            if not result['key_logic']:
                print("❌ FAIL: Key Logic is empty (Expected content from inline text)")
            elif "- [실적]" not in result['key_logic']:
                 print("❌ FAIL: Key Logic missing inline content")
            else:
                print("✅ PASS: Key Logic parsed correctly.")

            if not result['detailed_analysis'] or result['detailed_analysis'] == result_text:
                 # Note: The current logic falls back to result_text if detailed_analysis is empty, 
                 # but we want it to extract the specific section.
                 # If it returns the whole text, it means parsing failed to extract the specific part.
                 if "긍정적인 흐름이 예상됩니다" not in result['detailed_analysis'] or len(result['detailed_analysis']) > 100:
                     print("❌ FAIL: Detailed Analysis not parsed correctly (likely empty or full text fallback)")
                 else:
                     print("✅ PASS: Detailed Analysis parsed correctly.")
            else:
                 print("✅ PASS: Detailed Analysis parsed.")

if __name__ == "__main__":
    test_parsing_logic()
