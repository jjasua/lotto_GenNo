import asyncio
import os
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

# MCP 서버 초기화
# FastMCP를 사용하여 간단하게 도구(Tool)를 노출하는 서버를 생성합니다.
mcp = FastMCP("LottoPurchaseServer")

@mcp.tool()
async def purchase_lotto(user_id: str, user_pw: str, numbers_list: list[list[int]]) -> str:
    """
    동행복권(dhlottery.co.kr) 사이트에 로그인하여 전달받은 로또 번호 5게임을 자동으로 구매합니다.
    
    Args:
        user_id: 동행복권 아이디
        user_pw: 동행복권 비밀번호
        numbers_list: 구매할 로또 번호 리스트 (예: [[1,2,3,4,5,6], [10,11,12,13,14,15], ...]) 최대 5게임
    """
    
    if not numbers_list or len(numbers_list) > 5:
        return "오류: 번호 조합은 1개 이상, 5개 이하로 전달해야 합니다."

    print(f"[{user_id}] 계정으로 로또 자동 구매 시작... (총 {len(numbers_list)} 게임)")
    
    # Playwright를 이용한 브라우저 자동화 시작
    async with async_playwright() as p:
        # headless=False로 설정하면 브라우저가 직접 뜨는 것을 볼 수 있습니다. (개발/디버깅 용도)
        # 봇 탐지 우회 및 팝업 대처를 위해 설정이 필요할 수 있습니다.
        browser = await p.chromium.launch(headless=False)
        
        # 새로운 브라우저 컨텍스트 생성
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            # 1. 동행복권 메인 페이지 및 로그인 페이지로 이동
            await page.goto("https://dhlottery.co.kr/user.do?method=login")
            
            # 2. 로그인 폼 채우기 및 로그인 버튼 클릭
            await page.fill('input[name="userId"]', user_id)
            await page.fill('input[name="password"]', user_pw)
            
            # 팝업 대처를 위해 Promise.all 사용 (클릭 후 이동 대기)
            async with page.expect_navigation():
                await page.click('a.btn_common.lrg.blu[onclick="javascript:check_if_Check()"]')
            
            # 로그인이 성공했는지 예치금 요소(잔액) 등이 표시되는지 확인
            try:
                await page.wait_for_selector('span.money', timeout=5000)
                money_text = await page.locator('span.money').inner_text()
                print(f"로그인 성공! 현재 예치금: {money_text}")
            except Exception as e:
                return "로그인 실패: 아이디/비밀번호를 확인하거나 사이트 캡차(보안)가 발생했을 수 있습니다."

            # 3. 로또 구매 페이지로 이동
            await page.goto("https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40")
            print("구매 페이지 접근 완료")
            
            # --- 실무 구현 포인트 (이하 코드는 동행복권 Iframe 구조에 맞춘 수도코드 형태입니다) ---
            # 동행복권 구매 페이지는 내부에 iframe으로 구성되어 있으므로 프레임을 찾아야 합니다.
            # frame = page.frame(name="ifrm_tab")
            # if not frame:
            #     return "구매 프레임을 찾을 수 없습니다."
            
            # 4. 각 번호 조합별 마우스 클릭 조작
            # for idx, nums in enumerate(numbers_list):
            #     # '혼합선택' 탭 클릭
            #     # 번호 클릭 (1~45번 div 레이블 찾아서 클릭)
            #     for num in nums:
            #         await frame.click(f'label[for="check645num{num}"]')
            #     # '확인' 버튼 클릭하여 조합 1게임 추가
            #     await frame.click('input#btnSelectNum')
            
            # 5. 구매하기 버튼 클릭
            # await frame.click('input#btnBuy')
            
            # 6. 구매 확인 팝업 (Alert) 처리
            # page.on("dialog", lambda dialog: dialog.accept())
            # ---------------------------------------------------------------------------------

            # 임시 대기 (브라우저 동작 확인용)
            await page.wait_for_timeout(3000)
            
            result_msg = f"성공적으로 처리되었습니다. (테스트 모드: 실제 결제는 비활성화 상태입니다. 전달된 게임수: {len(numbers_list)})"
            return result_msg
            
        except Exception as e:
            print(f"에러 발생: {e}")
            return f"오류 발생: {str(e)}"
        
        finally:
            await browser.close()


if __name__ == "__main__":
    # MCP 서버 실행 (stdio 방식으로 LLM과 통신 대기)
    print("동행복권 MCP 서버를 시작합니다...")
    mcp.run(transport="stdio")
