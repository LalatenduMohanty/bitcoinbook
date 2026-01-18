# Building the PDF

This guide explains how to generate a PDF version of "Mastering Bitcoin: Programming the Open Blockchain (3rd Edition)" from the AsciiDoc source files.

## Prerequisites

You need one of the following container runtimes installed:

- **Podman** (recommended for Fedora/RHEL)
- **Docker**

## Quick Start

### Using Podman

```bash
podman run --rm -v "$(pwd)":/documents:Z \
  docker.io/asciidoctor/docker-asciidoctor \
  asciidoctor-pdf \
  -a source-highlighter=rouge \
  -a icons=font \
  /documents/book.adoc \
  -o /documents/mastering-bitcoin-3rd-edition.pdf
```

### Using Docker

```bash
docker run --rm -v "$(pwd)":/documents \
  asciidoctor/docker-asciidoctor \
  asciidoctor-pdf \
  -a source-highlighter=rouge \
  -a icons=font \
  /documents/book.adoc \
  -o /documents/mastering-bitcoin-3rd-edition.pdf
```

## Options Explained

| Option | Description |
|--------|-------------|
| `--rm` | Remove the container after execution |
| `-v "$(pwd)":/documents` | Mount current directory into the container |
| `:Z` | SELinux label (required for Podman on Fedora/RHEL) |
| `-a source-highlighter=rouge` | Enable syntax highlighting for code blocks |
| `-a icons=font` | Use Font Awesome icons |
| `/documents/book.adoc` | Input file (the main book file) |
| `-o /documents/mastering-bitcoin.pdf` | Output PDF file |

## Additional Options

### Table of Contents

Add a table of contents on the left side:

```bash
-a toc=left -a toclevels=3
```

### Section Numbering

Enable numbered sections:

```bash
-a sectnums -a sectnumlevels=3
```

### Full Example with All Options

```bash
podman run --rm -v "$(pwd)":/documents:Z \
  docker.io/asciidoctor/docker-asciidoctor \
  asciidoctor-pdf \
  -a source-highlighter=rouge \
  -a icons=font \
  -a toc=left \
  -a toclevels=3 \
  -a sectnums \
  -a sectnumlevels=3 \
  /documents/book.adoc \
  -o /documents/mastering-bitcoin-3rd-edition.pdf
```

## Alternative: Local Installation

If you prefer not to use containers, you can install Asciidoctor locally:

### Install Ruby and Asciidoctor

**On Fedora/RHEL:**
```bash
sudo dnf install ruby rubygems ruby-devel
gem install asciidoctor asciidoctor-pdf rouge
```

**On Ubuntu/Debian:**
```bash
sudo apt install ruby ruby-dev rubygems
gem install asciidoctor asciidoctor-pdf rouge
```

**On macOS:**
```bash
brew install ruby
gem install asciidoctor asciidoctor-pdf rouge
```

### Generate PDF Locally

```bash
asciidoctor-pdf \
  -a source-highlighter=rouge \
  -a icons=font \
  book.adoc \
  -o mastering-bitcoin-3rd-edition.pdf
```

## Output

The generated PDF will be created in the current directory with the specified filename (`mastering-bitcoin-3rd-edition.pdf`).

## Generating HTML for Kindle

To publish on Amazon Kindle Direct Publishing (KDP), you can generate an HTML version of the book.

### Generate HTML

```bash
podman run --rm -v "$(pwd)":/documents:Z \
  docker.io/asciidoctor/docker-asciidoctor \
  asciidoctor \
  -a source-highlighter=rouge \
  -a icons=font \
  -a toc=left \
  -a toclevels=3 \
  /documents/book.adoc \
  -o /documents/mastering-bitcoin-3rd-edition.html
```

### Create ZIP Package for KDP Upload

KDP requires images to be bundled with HTML. Create a ZIP file:

```bash
zip -r mastering-bitcoin-3rd-edition-kindle.zip \
  mastering-bitcoin-3rd-edition.html \
  images/
```

### Supported Kindle Formats

According to [Amazon KDP](https://kdp.amazon.com/en_US/help/topic/G200634390), supported formats include:

| Format | Notes |
|--------|-------|
| **HTML (ZIP)** | Best for technical books with code |
| **EPUB** | Standard eBook format |
| **DOC/DOCX** | Simple text-heavy books |
| **KPF** | Created with Kindle Create tool |
| **PDF** | Print Replica only (English supported) |

### Tips for Kindle Publishing

1. **Validate with Kindle Previewer** - Download from Amazon to test your book
2. **Check images** - Ensure all images are included in the ZIP
3. **Table of Contents** - The generated HTML includes a navigable TOC
4. **Code blocks** - Syntax highlighting is preserved in HTML

## Generating DOCX (Microsoft Word)

To generate a DOCX file, first create the HTML then convert using Pandoc:

### Step 1: Generate HTML (if not already done)

```bash
podman run --rm -v "$(pwd)":/documents:Z \
  docker.io/asciidoctor/docker-asciidoctor \
  asciidoctor \
  -a source-highlighter=rouge \
  -a icons=font \
  /documents/book.adoc \
  -o /documents/mastering-bitcoin-3rd-edition.html
```

### Step 2: Convert HTML to DOCX using Pandoc

```bash
podman run --rm -v "$(pwd)":/data:Z \
  docker.io/pandoc/latex:latest \
  -f html -t docx \
  /data/mastering-bitcoin-3rd-edition.html \
  -o /data/mastering-bitcoin-3rd-edition.docx
```

### Using Docker instead of Podman

```bash
docker run --rm -v "$(pwd)":/data \
  pandoc/latex:latest \
  -f html -t docx \
  /data/mastering-bitcoin-3rd-edition.html \
  -o /data/mastering-bitcoin-3rd-edition.docx
```

### Notes on DOCX Output

- Images are embedded directly in the DOCX file
- Code syntax highlighting is preserved
- Table of contents may need manual adjustment in Word
- Good for reviewers who prefer Microsoft Word

## Troubleshooting

### SELinux Issues (Podman)

If you encounter permission errors on Fedora/RHEL, ensure you're using the `:Z` suffix on the volume mount:

```bash
-v "$(pwd)":/documents:Z
```

### Missing Fonts

If you see font-related warnings, the default fonts should work fine. For custom fonts, you can create a custom theme file.

### Image Path Issues

If images aren't rendering, you can explicitly set the images directory:

```bash
-a imagesdir=/documents/images
```

## Book Structure

The main entry point is `book.adoc`, which includes:

- Preface
- 14 Chapters (ch01-ch14)
- 3 Appendices (appa-appc)
- Glossary

## License

This book is licensed under [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).

