# Frontend Icon Replacement Guide

Here is a complete guide to replacing the standard icons in the QCanvas frontend with premium, custom alternatives. 

## 1. Where to Download Free Premium Icons

Here is a curated list of websites offering high-quality, modern, and free (or freemium) icons that can elevate your UI design from standard to premium:

1. **Flaticon**
   - **Website:** [flaticon.com](https://www.flaticon.com)
   - **Why it's great:** The largest database of free customizable icons in the world. Great for detailed, colorful, or 3D-style UI icons.
2. **Iconscout**
   - **Website:** [iconscout.com](https://iconscout.com)
   - **Why it's great:** Offers incredible 3D icons, Lottie animations, and highly premium vector illustrations with free tiers available.
3. **Icons8**
   - **Website:** [icons8.com](https://icons8.com)
   - **Why it's great:** Offers consistent icon packs in numerous modern styles (e.g., Glassmorphism, iOS, Material, 3D fluents).
4. **Heroicons** 
   - **Website:** [heroicons.com](https://heroicons.com)
   - **Why it's great:** Hand-crafted, very sleek SVG icons by the makers of Tailwind CSS. Excellent for a clean, minimalist, professional look.
5. **Phosphor Icons**
   - **Website:** [phosphoricons.com](https://phosphoricons.com)
   - **Why it's great:** A highly flexible icon family that lets you customize weights and styles (Thin, Light, Regular, Bold, Fill, Duotone) dynamically.

## 2. Best Format & Resolution

To ensure the icons look perfectly sharp on all screens (including high-DPI Retina/4K displays) and don't slow down the application:

* **Recommended Format:** **SVG (Scalable Vector Graphics)**
  * **Why:** SVGs are code, not pixels. They are completely losslessly scalable, very lightweight, and load instantly. You can also easily change their colors dynamically via CSS (`fill="currentColor"`).
* **If you absolutely must use Raster/Pixel Images (like 3D icons):**
  * **Recommended Format:** **WebP** or **PNG** (with transparent backgrounds). WebP is preferred for significantly smaller file sizes.
  * **Best Resolution:** **128x128 px** or **256x256 px** (for retina support). Even though they usually display at ~`24x24 px` in the UI, having structural assets scaled down from larger sizes prevents blurring on modern high-resolution monitors. 

## 3. The Complete List of Required Icons

Based on the frontend source code, here are all the unique `lucide-react` standard icons currently used across the application. You will need replacements for these conceptual representations:

### App Navigation & General UI
- `ArrowLeft`, `ArrowRight`, `ChevronDown`, `ChevronRight`, `ChevronUp`, `MoreHorizontal`
- `Menu`, `Plus`, `RefreshCw`, `X`, `XCircle`, `Check`, `CheckCircle`, `CheckCircle2`
- `Maximize2`, `Minimize2`

### User Profile & Authentication
- `User`, `Users`, `LogOut`, `Lock`, `Mail`, `Eye`, `EyeOff`, `Edit2`
- `MapPin`, `Calendar`, `Camera`, `Shield`

### Editor & Development Tools
- `Code`, `Code2`, `Terminal`, `Regex`, `WholeWord`, `GitBranch`, `Github`
- `Database`, `Server`, `Settings`, `Wrench`, `Search`, `Replace`, `Copy`, `Save`, `Download`, `Upload`
- `File`, `FileCode`, `FileCode2`, `FileIcon`, `FileText`, `Folder`, `FolderPlus`

### Science & Quantum Concepts
- `Atom`, `CircuitBoard`, `Cpu`, `Sparkles`, `Zap`

### Analytics & Gamification
- `Award`, `Trophy`, `Target`, `TrendingUp`, `BarChart2`, `BarChart3`
- `Activity`, `Star`, `Flame`, `Rocket`

### Content & Communication
- `BookCheck`, `BookOpen`, `Layers`, `Lightbulb`, `Share2`, `Tag`
- `AlertCircle`, `AlertTriangle`, `HelpCircle`, `Info`, `Globe`, `Languages`
- `Linkedin`

### Display & Media
- `Monitor`, `Cloud`, `Clock`, `Loader2`, `Play`, `Repeat`, `Trash2`
- `Moon`, `Sun` (Dark/Light mode toggles)

---
> [!TIP]
> **Implementation Strategy:** Once you download your SVGs, the best way to integrate them is to create custom React wrapper components for each SVG, mirroring how the current `lucide-react` imports are imported and styled. This allows seamless drop-in replacements!
