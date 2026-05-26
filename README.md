# Neo_Legend_Project




球场投射图：
![alt text](6f95be795cc16e2d3b0e0f6425e12353.jpg)
![alt text](542b1ddcb7b0ed0c8748915c4ab50e0a.jpg)
![alt text](3e55ac98f1a65823dc9cecadfed47db8.jpg)
![alt text](8f8f3a2852825db7c630dec71b0a0cb9.jpg)
![alt text](10243b5d8a83a1d45b8d6ca9a054db51.jpg)
![alt text](57eb5f6214055a593ff7c238e220f944.jpg)
![alt text](248a28494b8e8bb6aea0999c7455b3bd.jpg)
![alt text](0ece60f1e357e60d332c2983bac940dd.jpg)
双球场投射图
![alt text](3c1084f8f059bd51ab35a52c527d08f5.jpg)
球场投射动态图gif
![alt text](0ca42dfeab11e52e7e4a3a1665b81695.jpg)

坐标图：
![alt text](fde04acdba96eb494b0e6563ebfee4c8.jpg)

正负坐标图：
![alt text](9e0f773e8e471b63088b5b85c482f5b8.jpg)

玫瑰图：
![alt text](4acb2531cd2856e6c84dde127fdbb514.jpg)

表格图：
![alt text](fe96ef95bd423017d90a51b1b8b2e445.jpg)
![alt text](a1cb23fc1b0420d211ffc5ad48ba5034.jpg)
![alt text](fe727949d4ad07c93ac950c9bc408e0d.jpg)
![alt text](106383dc3bf1a2bee4c19e7d6f87573f.jpg)


根据上面的图形读取图形的样式，然后根据图形的布局使用Python绘制一个fast-api对外的接口，用于绘制图形。
要求1：在图形样式上要与图例中的保持一致，而且每种类型的图例分别生成对应独立的skills ，用来后期独立的控制skills，
要求2：生成全套的图例测试用例
要求3：自动选择绘制图例的组件，根据图例的类型自动选择对应的组件。
要求4：在接口中添加一个参数，用来指定要绘制的图例的类型。
要求5：在接口中添加一个参数，用来指定要绘制的图例的样式。

## 批量生成与调参日志

生成全部图例图片、模拟数据、参考图比对报告和调参日志：

```powershell
$env:PYTHONPATH='src'
python -m neo_legend.batch_generate --output-dir 'G:\echaet' --project-root 'E:\haochenkeji\Neo_Legend_Project'
```

输出内容：

- `G:\echaet\*.png` / `G:\echaet\*.gif`：每种图例样式的最终图片。
- `G:\echaet\raw\*`：未经自动后处理的原始渲染图片。
- `G:\echaet\logs\render_events.jsonl`：逐图例生成日志，包含请求参数、模拟数据摘要、图片指标、参考图比对和调参因子。
- `G:\echaet\logs\comparison_report.json`：结构化比对报告。
- `G:\echaet\logs\tuning_report.md`：人工微调用报告。

FastAPI 也提供 `POST /batch-generate` 用于从 Swagger 页面触发同样流程。
