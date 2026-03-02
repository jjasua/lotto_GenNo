import { useState, useMemo } from 'react'
import lottoData from './assets/lotto_data.json'
import './App.css'

type Draw = {
  draw: number;
  numbers: number[];
  bonus: number;
};

// lottoData is sorted by draw desc.
const typedLottoData = lottoData as Draw[];

function App() {
  const [recommendedGroups, setRecommendedGroups] = useState<number[][]>([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [algorithm, setAlgorithm] = useState<'random' | 'frequent' | 'balanced'>('balanced');

  // Compute number frequencies
  const frequencies = useMemo(() => {
    const counts = new Array(46).fill(0);
    typedLottoData.forEach(d => {
      d.numbers.forEach(n => {
        counts[n]++;
      });
    });
    return counts;
  }, []);

  const getLottoColor = (num: number) => {
    if (num <= 10) return '#fbc400';
    if (num <= 20) return '#69c8f2';
    if (num <= 30) return '#ff7272';
    if (num <= 40) return '#aaa';
    return '#b0d840';
  };

  const generateNumbers = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setRecommendedGroups([]);

    setTimeout(() => {
      const newGroups: number[][] = [];

      for (let g = 0; g < 5; g++) {
        const nums: Set<number> = new Set();

        if (algorithm === 'random') {
          while (nums.size < 6) {
            nums.add(Math.floor(Math.random() * 45) + 1);
          }
        } else if (algorithm === 'frequent') {
          // Weighted random based on frequencies
          const totalFreq = frequencies.reduce((a, b) => a + b, 0);
          while (nums.size < 6) {
            let rand = Math.random() * totalFreq;
            for (let i = 1; i <= 45; i++) {
              rand -= frequencies[i];
              if (rand <= 0) {
                nums.add(i);
                break;
              }
            }
          }
        } else if (algorithm === 'balanced') {
          // Mix of frequent and infrequent numbers
          const sortedNums = Array.from({ length: 45 }, (_, i) => i + 1).sort((a, b) => frequencies[b] - frequencies[a]);
          const hotPool = sortedNums.slice(0, 15);
          const coldPool = sortedNums.slice(30, 45);
          const randomPool = sortedNums.slice(15, 30);

          while (nums.size < 3) nums.add(hotPool[Math.floor(Math.random() * hotPool.length)]);
          while (nums.size < 5) nums.add(coldPool[Math.floor(Math.random() * coldPool.length)]);
          while (nums.size < 6) nums.add(randomPool[Math.floor(Math.random() * randomPool.length)]);
          // Fill remaining if needed
          while (nums.size < 6) nums.add(Math.floor(Math.random() * 45) + 1);
        }

        newGroups.push(Array.from(nums).sort((a, b) => a - b));
      }

      setRecommendedGroups(newGroups);
      setIsAnimating(false);
    }, 800);
  };

  const resetNumbers = () => {
    setRecommendedGroups([]);
  };

  return (
    <div className="container">
      <div className="glass-card">
        <header className="header">
          <h1 className="title">🍀 행운의 로또 번호 추천기</h1>
          <p className="subtitle">
            역대 {typedLottoData.length}회차 당첨 데이터를 기반으로 번호를 추출합니다.
          </p>
        </header>

        <main className="main-content">
          <div className="options">
            <label className="option-label">
              <span className="option-text">추천 방식 선택</span>
              <select className="select-box" value={algorithm} onChange={(e) => setAlgorithm(e.target.value as 'random' | 'frequent' | 'balanced')}>
                <option value="balanced">🔮 황금 밸런스 (많이 나온 수 + 적게 나온 수 조합)</option>
                <option value="frequent">🔥 확률 집중 (비율 기반 가중치 추첨)</option>
                <option value="random">🎲 완전 무작위 (순수 확률)</option>
              </select>
            </label>
          </div>

          <div className="result-area">
            {recommendedGroups.length === 0 && !isAnimating ? (
              <div className="placeholder">버튼을 눌러 번호를 받아보세요!</div>
            ) : isAnimating ? (
              <div className="loader">행운의 번호를 분석 중입니다...</div>
            ) : (
              <div className="balls-groups-container">
                {recommendedGroups.map((group, groupIdx) => (
                  <div key={groupIdx} className="balls-group-row">
                    <div className="group-label">조합 {groupIdx + 1}</div>
                    <div className="balls-container">
                      {group.map((num, idx) => (
                        <div
                          key={idx}
                          className="lotto-ball animate-pop"
                          style={{
                            backgroundColor: getLottoColor(num),
                            animationDelay: `${groupIdx * 0.1 + idx * 0.05}s`
                          }}
                        >
                          {num}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="button-group">
            <button
              className={`generate-btn ${isAnimating ? 'disabled' : ''}`}
              onClick={generateNumbers}
              disabled={isAnimating}
            >
              {isAnimating ? '생성 중...' : '번호 추첨하기'}
            </button>
            {recommendedGroups.length > 0 && !isAnimating && (
              <button className="reset-btn" onClick={resetNumbers}>
                초기화
              </button>
            )}
          </div>
        </main>

        <footer className="footer">
          최근 회차 ({typedLottoData[0].draw}회) 당첨 번호: {typedLottoData[0].numbers.join(', ')} (보너스: {typedLottoData[0].bonus})
        </footer>
      </div>
    </div>
  )
}

export default App
