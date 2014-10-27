## makefile for decode.C
INPUT		 := /scratch/PAD-testbeams/CERN_oct_14/pad_out
OUTPUT		 := results/
ANALYSIS	 := plotting.py
OPTIONS		 := 
INPUT_FINAL  := input
PICS_OUT	 := /scratch/analysis/output/PAD/
FNAME        := run_*.root
FDIR         := $(INPUT)/$(FNAME)
SOURCES      := $(wildcard $(INPUT)/run_*.root)
SOURCES_FINAL:= $(patsubst $(INPUT)/%.root,$(INPUT_FINAL)/%.root,$(SOURCES))
OBJECTS      := $(patsubst $(INPUT)/%.root,$(OUTPUT)/%.txt,$(SOURCES))
RM  	     := rm
MV      	 := mv

# Rules ====================================
#all: $(SOURCES) $(EXECUTABLE)
all: printer  analysis
#all: analysis

printer:
	@echo 'INPUT $(INPUT)'
	@echo 'OUTPUT $(OUTPUT)'
	@echo 'SOURCES $(SOURCES)'
	@echo 'FNAME $(FNAME)'
	@echo 'FDIR $(FDIR)'
	@echo 'INPUT_FINAL $(INPUT_FINAL)'
	@echo 'SOURCES_FINAL $(SOURCES_FINAL)'
	@echo ''
	@echo 'OBJECTS $(OBJECTS)'
	@echo ''

analysis: $(OBJECTS) $(ANALYSIS)

$(OBJECTS): |$(OUTPUT)

$(OUTPUT):
	mkdir -p $(OUTPUT)

$(INPUT_FINAL)/%.root: 
	ln -s $(patsubst $(INPUT_FINAL)/%.root,$(INPUT)/%.root,$@) $@

$(OUTPUT)/%.txt:  $(INPUT_FINAL)/%.root $(ANALYSIS)
	@echo 'i $<'
	@echo '@ $@'
	@echo '%% %'
	python $(ANALYSIS)  $(OPTIONS)  $<
	touch $@
## $(EXECUTABLE): $(OBJECTS)
## 	$(CC) $(LDFLAGS) -o $@ $<  $(LIBS)

clean:
	find $(SRCDIR) -name '*.o' -exec $(RM) -v {} ';' 
	$(RM) decode

