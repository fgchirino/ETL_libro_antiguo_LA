import os
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pandas as pd
import textwrap

def graficar_torta(valores, etiquetas, colores, titulo, ruta_out):
    if sum(valores) == 0: return
    total = sum(valores)
    etiquetas_fmt = [f"{textwrap.fill(str(etq), width=18)}\n({(val/total):.1%})" for etq, val in zip(etiquetas, valores)]
    
    plt.figure(figsize=(10, 10))
    plt.pie(valores, labels=etiquetas_fmt, startangle=140, colors=colores, 
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
            textprops={'fontsize': 10, 'fontweight': 'bold', 'color': '#2C3E50'})
    
    plt.title(titulo, fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig(ruta_out, dpi=300)
    plt.close()

def graficar_barras_verticales(serie, titulo, eje_x, eje_y, color, ruta_out):
    if serie.empty: return
    plt.figure(figsize=(12, 6))
    plt.bar(serie.index.astype(str), serie.values, color=color, edgecolor='white')
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel(eje_x, fontsize=12)
    plt.ylabel(eje_y, fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(ruta_out, dpi=300)
    plt.close()

def graficar_histograma(serie, bins, titulo, eje_x, eje_y, color, ruta_out):
    if serie.empty: return
    plt.figure(figsize=(12, 5))
    plt.hist(serie, bins=bins, color=color, edgecolor='white', alpha=0.9)
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel(eje_x)
    plt.ylabel(eje_y)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(ruta_out, dpi=300)
    plt.close()

def graficar_heatmap(df_cron, titulo, ruta_out, rango_decadas):
    if df_cron.empty: return
    matriz = df_cron.pivot_table(index='digito_anio', columns='Decada', values='ID_Manifestacion', aggfunc='count')
    matriz = matriz.reindex(index=range(10), columns=rango_decadas, fill_value=0)
    
    plt.figure(figsize=(16, 6))
    sns.heatmap(matriz, cmap="YlOrBr", linewidths=.5, linecolor='white', cbar_kws={'label': 'Nº Ediciones'})
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel('Décadas')
    plt.ylabel('Terminación del Año (0-9)')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(ruta_out, dpi=300)
    plt.close()

def graficar_barras_horizontales(serie, titulo, color, ruta_out):
    if serie.empty: return
    plt.figure(figsize=(12, 8))
    ax = serie.iloc[::-1].plot(kind='barh', color=color)
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel('Frecuencia')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(ruta_out, dpi=300)
    plt.close()

def graficar_pareto(serie, titulo, color_barras, color_linea, ruta_out):
    if serie.empty: return
    total = serie.sum()
    df_pareto = pd.DataFrame({'frecuencia': serie})
    df_pareto['acumulado_pct'] = (df_pareto['frecuencia'].cumsum() / total) * 100
    df_p_head = df_pareto.head(25)

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.bar(df_p_head.index.astype(str), df_p_head['frecuencia'], color=color_barras)
    ax1.set_ylabel('Frecuencia Absoluta', color=color_barras, fontweight='bold')
    plt.xticks(rotation=45, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(df_p_head.index.astype(str), df_p_head['acumulado_pct'], color=color_linea, marker='o', linewidth=2)
    ax2.set_ylabel('% Acumulado', color=color_linea, fontweight='bold')
    ax2.set_ylim(0, 110)
    ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.5)

    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(ruta_out, dpi=300)
    plt.close()

def graficar_red_semantica(G, frecuencia_nodos, tipo_nodos, mapa_colores, min_apariciones, color_aristas, color_texto, ruta_out):
    if len(G.nodes()) == 0: return
    plt.figure(figsize=(24, 18)) 
    
    # Ajuste físico: k=0.4 evita que los nodos aislados aplasten el centro
    pos = nx.spring_layout(G, k=0.4, iterations=100, seed=42) 
    
    # 1. Dibujar Aristas
    if len(G.edges()) > 0:
        weights = [G[u][v]['weight'] * 1.5 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=weights, alpha=0.3, edge_color=color_aristas)

    # 2. Dibujar Nodos
    sizes = [frecuencia_nodos.get(node, 1) * 150 for node in G.nodes()]
    colores_nodos = [mapa_colores.get(tipo_nodos.get(node), '#95a5a6') for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colores_nodos, alpha=0.9, edgecolors='white', linewidths=1.5)
    
    # 3. Etiquetas con Offset dinámico (Bbox transparente)
    # Calcula el alto del grafo para desplazar el texto proporcionalmente hacia arriba
    y_values = [v[1] for v in pos.values()]
    offset = (max(y_values) - min(y_values)) * 0.015 if y_values else 0.05
    pos_labels = {k: (v[0], v[1] + offset) for k, v in pos.items()} 
    
    estilo_caja = dict(boxstyle="round,pad=0.2", ec="none", fc="white", alpha=0.75)
    
    nx.draw_networkx_labels(G, pos_labels, font_size=10, font_weight='bold', 
                            font_color=color_texto, bbox=estilo_caja)

    plt.title(f'Red de Co-Ocurrencia Temática (Vínculos >= {min_apariciones})', fontsize=18, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(ruta_out, dpi=300, bbox_inches='tight')
    plt.close()