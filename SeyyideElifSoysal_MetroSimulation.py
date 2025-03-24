from collections import defaultdict, deque
import heapq
from typing import Dict, List, Set, Tuple, Optional
import networkx as nx
import matplotlib.pyplot as plt

class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.komsular: List[Tuple['Istasyon', int]] = []

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        self.komsular.append((istasyon, sure))

class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)

    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        if idx not in self.istasyonlar:
            istasyon = Istasyon(idx, ad, hat)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)
    
    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]

        kuyruk = deque([(baslangic, [baslangic], baslangic.hat)])
        ziyaret_edilenler = set()

        while kuyruk:
            mevcut_istasyon, rota, mevcut_hat = kuyruk.popleft()

            if mevcut_istasyon.idx == hedef.idx:
                return rota

            ziyaret_edilenler.add(mevcut_istasyon.idx)

            for komsu, _ in mevcut_istasyon.komsular:
                if komsu.idx not in ziyaret_edilenler:
                    yeni_aktarma = mevcut_hat != komsu.hat
                    yeni_rota = rota + [komsu]
                    kuyruk.append((komsu, yeni_rota, komsu.hat if yeni_aktarma else mevcut_hat))

        return None

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]

        pq = [(0, id(baslangic), baslangic, [baslangic])]
        en_kisa_sureler = {baslangic.idx: 0}

        while pq:
            toplam_sure, _, mevcut_istasyon, rota = heapq.heappop(pq)

            if mevcut_istasyon.idx == hedef.idx:
                return rota, toplam_sure

            for komsu, sure in mevcut_istasyon.komsular:
                yeni_sure = toplam_sure + sure

                if komsu.idx not in en_kisa_sureler or yeni_sure < en_kisa_sureler[komsu.idx]:
                    en_kisa_sureler[komsu.idx] = yeni_sure
                    yeni_rota = rota + [komsu]
                    heapq.heappush(pq, (yeni_sure, id(komsu), komsu, yeni_rota))

        return None

    def metro_grafik_ciz(self, metro, rotalar=None):
        G = nx.Graph()

        # Düğümler (İstasyonlar)
        for istasyon in metro.istasyonlar.values():
            G.add_node(istasyon.idx, label=istasyon.ad, color=istasyon.hat)

        # Kenarları (Bağlantılar)
        for istasyon in metro.istasyonlar.values():
            for komsu, sure in istasyon.komsular:
                G.add_edge(istasyon.idx, komsu.idx, weight=sure)

        # Hatlar için renkler
        hat_renkleri = {
            "Kırmızı Hat": "#FF0000",
            "Mavi Hat": "#0000FF",
            "Turuncu Hat": "#FFA500"
        }

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, seed=42)

        # Node renkleri (hatlara göre)
        colors = [hat_renkleri[G.nodes[n]["color"]] for n in G.nodes]

        edge_colors = ["gray"] * len(G.edges)

        if rotalar:
            for rota in rotalar:
                for i in range(len(rota) - 1):
                    edge_colors[G.edges[rota[i].idx, rota[i+1].idx]] = "green"

        # Grafik
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color=colors, edge_color=edge_colors, font_size=10, font_weight="bold")
        labels = {n: G.nodes[n]["label"] for n in G.nodes}
        label_pos = {n: (x, y + 0.12) for n, (x, y) in pos.items()}
        nx.draw_networkx_labels(G, label_pos, labels)
        plt.title("Metro Ağı Görselleştirme")
        plt.show()



# Örnek Kullanım
if __name__ == "__main__":
    metro = MetroAgi()
    
    # İstasyonlar ekleme
    # Kırmızı Hat
    metro.istasyon_ekle("K1", "Kızılay", "Kırmızı Hat")
    metro.istasyon_ekle("K2", "Ulus", "Kırmızı Hat")
    metro.istasyon_ekle("K3", "Demetevler", "Kırmızı Hat")
    metro.istasyon_ekle("K4", "OSB", "Kırmızı Hat")
    
    # Mavi Hat
    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat")
    metro.istasyon_ekle("M2", "Kızılay", "Mavi Hat")  # Aktarma noktası
    metro.istasyon_ekle("M3", "Sıhhiye", "Mavi Hat")
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat")
    
    # Turuncu Hat
    metro.istasyon_ekle("T1", "Batıkent", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat")  # Aktarma noktası
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat")  # Aktarma noktası
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat")
    
    # Bağlantılar ekleme
    # Kırmızı Hat bağlantıları
    metro.baglanti_ekle("K1", "K2", 4)  # Kızılay -> Ulus
    metro.baglanti_ekle("K2", "K3", 6)  # Ulus -> Demetevler
    metro.baglanti_ekle("K3", "K4", 8)  # Demetevler -> OSB
    
    # Mavi Hat bağlantıları
    metro.baglanti_ekle("M1", "M2", 5)  # AŞTİ -> Kızılay
    metro.baglanti_ekle("M2", "M3", 3)  # Kızılay -> Sıhhiye
    metro.baglanti_ekle("M3", "M4", 4)  # Sıhhiye -> Gar
    
    # Turuncu Hat bağlantıları
    metro.baglanti_ekle("T1", "T2", 7)  # Batıkent -> Demetevler
    metro.baglanti_ekle("T2", "T3", 9)  # Demetevler -> Gar
    metro.baglanti_ekle("T3", "T4", 5)  # Gar -> Keçiören
    
    # Hat aktarma bağlantıları (aynı istasyon farklı hatlar)
    metro.baglanti_ekle("K1", "M2", 2)  # Kızılay aktarma
    metro.baglanti_ekle("K3", "T2", 3)  # Demetevler aktarma
    metro.baglanti_ekle("M4", "T3", 2)  # Gar aktarma
    
    # Test senaryoları
    print("\n=== Test Senaryoları ===")
    
    # Senaryo 1: AŞTİ'den OSB'ye
    print("\n1. AŞTİ'den OSB'ye:")
    rota = metro.en_az_aktarma_bul("M1", "K4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("M1", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 2: Batıkent'ten Keçiören'e
    print("\n2. Batıkent'ten Keçiören'e:")
    rota = metro.en_az_aktarma_bul("T1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 3: Keçiören'den AŞTİ'ye
    print("\n3. Keçiören'den AŞTİ'ye:")
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Grafik fonksiyonunu çağırma
metro.metro_grafik_ciz(metro)
